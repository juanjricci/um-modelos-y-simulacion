import signal
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np
import celery_calc
from mpl_toolkits.mplot3d import axes3d
import random as rnd
import socket
import multiprocessing
import time
import json
import argparse as ap
import psycopg2
from datetime import datetime


signal.signal(signal.SIGCHLD, signal.SIG_IGN)

parser = ap.ArgumentParser()
parser.add_argument('--config', type=str,
                    help='Ruta al archivo de configuracion', required=True)
args = parser.parse_args()

# cargo el archivo de configuracion en modo lectura
with open(args.config, 'r') as f:
    config = json.load(f)

# info para la conexion a la database obtenida del archivo config
hostname = config["hostname"]
username = config["username"]
password = config["password"]
database = config["database"]

# me conecto a la DB postgresql
myConnection = psycopg2.connect(
    host=hostname, user=username, password=password, dbname=database
)
cursor = myConnection.cursor()

# query para crear las tablas en la DB
create_tables_query = (
    """CREATE TABLE IF NOT EXISTS sim_data (
            id serial PRIMARY KEY,
            velocidad_viento float(4),
            angulo_viento float(4),
            duracion_viento float(4),
            tiempo_vuelo float(4),
            altura_maxima float(4),
            ultima_x float(2),
            ultima_y float(2),
            fecha DATE,
            hora TIME,
            id_cliente int
    );""",
    """CREATE TABLE IF NOT EXISTS dispersion (
            id_cliente int,
            dispersion float(4),
            fecha DATE
    );"""
)

for query in create_tables_query:
    # ejecuto la consulta
    cursor.execute(query)
myConnection.commit()
myConnection.close()

# creo un socket para la conexion cliente/servidor
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# socket.AF_INET -> sockets tcp/ip
# socket.SOCK_STREAM -> socket tcp, orientado a la conexion (flujo de datos)

# obtengo los datos para la conexion del archivo de configuracion
host = config["host"]
port = config["port"]
print(f'Waiting for conection (host: {host}, port: {port})...')

# enlazo el socket con la direccion
serversocket.bind((host, port))
serversocket.listen(2)
# socket.listen([backlog]) habilita al servidor a recibir conexiones.
# el backlog sirve para definir la cantidad de conexiones inaceptables permitidas.
# cuando se llegue a ese numero, el servidor no aceptara mas conexiones.

dispersion = []

# obtengo una lista de colores del archivo de configuracion.
# color = config["color"]
# color = ['red', 'green', 'blue', 'yellow',
#          'black', 'gray', 'pink', 'purple', 'orange']


def calcular_puntos(tiempo, tick, vz, vx, vy, x, y, z,
                    zviento, wind_duration, rx, ry,
                    duracion, ax, dot_color, vi, a, b, wind,
                    wind_angle, client_number,
                    cursor, hmax, cs, fecha, hora):

    # por cada iteracion calcula una posicion y la grafica
    while True:
        tiempo = tiempo + tick
        # la velocidad en z es variable
        vz = celery_calc.vz_variable.delay(vz, tick).get()
        x = celery_calc.pos_x.delay(x, vx, tick).get()
        y = celery_calc.pos_y.delay(y, vy, tick).get()
        z = celery_calc.pos_z.delay(z, vz, tick).get()
        if z <= 0:
            dispersion.append([x, y])
            break
        ax.scatter(x, y, z, c=dot_color, marker='o')
        plt.draw()
        plt.pause(0.0001)

        if z > zviento.get():
            while duracion < wind_duration:
                tiempo = tiempo + tick
                duracion = duracion + tick
                vx = rx.get()
                vy = ry.get()
                vz = celery_calc.vz_variable.delay(vz, tick).get()
                x = celery_calc.pos_x.delay(x, vx, tick).get()
                y = celery_calc.pos_y.delay(y, vy, tick).get()
                z = celery_calc.pos_z.delay(z, vz, tick).get()
                ax.scatter(x, y, z, c=dot_color, marker='o')
                plt.draw()
                plt.pause(0.0001)

    query = """ INSERT INTO sim_data (
        velocidad_viento, angulo_viento, duracion_viento,
        tiempo_vuelo, altura_maxima, ultima_x, ultima_y,
        fecha, hora, id_cliente
        ) VALUES (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s 
        )"""
    valores_insertar = (wind, wind_angle,wind_duration,
                        tiempo, hmax, x, y, fecha, hora,
                        client_number)
    cursor.execute(query, valores_insertar)


def plot(vi, a, b, wind, wind_angle, dot_color, ax, wind_duration,
         cs, client_number, cursor, fecha, hora):

    # calculos de componentes del vector velocidad
    velx = celery_calc.vel_x.delay(vi, a, b)
    vely = celery_calc.vel_y.delay(vi, a, b)
    velz = celery_calc.vel_z.delay(vi, a)

    # calculo de la altura del viento ( 2/3 de la altura maxima )
    zviento = celery_calc.altura_viento.delay(velz.get())
    # calculo de la altura maxima
    hmax = zviento.get()/(2/3)

    # tick de tiempo
    tick = 0.05

    # calculos de componentes del vector velocidad del viento
    wx = celery_calc.wind_x.delay(wind, wind_angle)
    wy = celery_calc.wind_y.delay(wind, wind_angle)

    # calculos de componentes del vector resultante
    rx = celery_calc.res_x.delay(velx.get(), wx.get())
    ry = celery_calc.res_x.delay(vely.get(), wy.get())

    x = 0
    y = 0
    z = 0
    vz = velz.get()
    vx = velx.get()
    vy = vely.get()

    tiempo = 0
    duracion = 0

    calcular_puntos(tiempo, tick, vz, vx, vy, x, y, z, zviento,
                    wind_duration, rx, ry, duracion, ax, dot_color,
                    vi, a, b, wind, wind_angle, client_number,
                    cursor, hmax, cs, fecha, hora)


def mp(clientsocket, client_number):

    # me conecto a la DB para empezar a agregarle datos
    myConnection = psycopg2.connect(
        host=hostname, user=username, password=password, dbname=database
    )
    cursor = myConnection.cursor()

    # declaracion de la figura y sus ejes
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    i = -1
    # el servidor recibe la informacion del cliente
    fecha = clientsocket.recv(1024).decode('utf-8')
    cantidad, vi, a, b = [int(i) for i in clientsocket.recv(2048).decode('utf-8').split('|')]
    # cantidad = int(clientsocket.recv(1024).decode())
    # vi = int(clientsocket.recv(1024).decode())
    # a = int(clientsocket.recv(1024).decode())
    # b = int(clientsocket.recv(1024).decode())
    while True:
        i += 1
        if i == cantidad:
            break
        # obtiene valores aleatorios del viento
        query = f"select * from viento WHERE fecha = '{fecha}'"
        cursor.execute(query)
        datos = cursor.fetchall()
        velocidad = datos[i][3]
        direccion = datos[i][2]
        hora = datos[i][1]
        print(f'Velocidad = {velocidad}')
        print(f'Direccion = {direccion}')
        #wind = rnd.randint(0, 10) # velocidad
        #wind_angle = rnd.randint(0, 360) # angulo
        wind_duration = rnd.uniform(0, 1) # duracion
        # envio la informacion del viento al cliente
        data = f"""
(Simulacion {i+1}) Valores del viento:\n\tVelocidad = {velocidad} m/s
\tAngulo = {direccion}\n\tDuracion = {wind_duration}\n\tFecha = {fecha}\n\tHora = {hora}
"""
        clientsocket.send(data.encode())
        # obtiene un color aleatorio para los puntos q se van a graficar
        red = rnd.random()
        green = rnd.random()
        blue = rnd.random()
        col = (red, green, blue)
        dot_color = np.array([col])
        # dot_color = color[rnd.randint(0, 25)]
        plot(vi, a, b, velocidad, direccion, dot_color,
             ax, wind_duration, clientsocket, client_number,
             cursor, fecha, hora)
    plt.savefig(f'grafico({client_number}).png')
    plt.show()

    mayor = 0
    j = 1
    # realizo el calculo de la dispersion
    for i in range(len(dispersion)):
        for j in range(len(dispersion)):
            l = celery_calc.disp.delay(dispersion, i, j).get()
            if l > mayor:
                mayor = l
        j = + 1

    # agrego los nuevos datos a la tabla dispersion
    query = """ INSERT INTO dispersion (
        id_cliente, dispersion, fecha
        ) VALUES (
            %s,%s,%s
        )"""
    valores_insertar = (client_number, mayor, fecha)
    cursor.execute(query, valores_insertar)
    # confirmo y cierro la conexion con la DB
    myConnection.commit()
    myConnection.close()
    # envio resultado de dispersion al cliente
    msg = f"Simulacion terminada.\nDistancia maxima entre puntos finales = {mayor} m"
    clientsocket.send(msg.encode())
    time.sleep(0.1)
    # envio señal para terminal la conexion con el cliente
    exit_signal = "exit"
    clientsocket.send(exit_signal.encode())
    clientsocket.close()
    


def multiP():
    client_number = -1
    while True:
        clientsocket, address = serversocket.accept()
        # acepta una conexion.
        # el socket debe estar enlazado a una direccion y
        # tmb debe estar escuchando para conexiones.
        print("Got a connection from %s" % str(address))
        client_number += 1
        print(f'Client number: {client_number}')
        # utilizo multiprocesamiento para que la aplicacion sea multicliente
        p = multiprocessing.Process(
            target=mp, args=(clientsocket, client_number))
        p.start()


if __name__ == "__main__":
    multiP()
