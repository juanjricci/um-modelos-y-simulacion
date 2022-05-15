import math
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

# quert para crear las tablas en la DB
create_tables_query = (
    """CREATE TABLE IF NOT EXISTS sim_data (
            id serial PRIMARY KEY,
            velocidad_inicial int,
            angulo_salida int,
            angulo_desviacion int,
            velocidad_viento int,
            angulo_viento int,
            duracion_viento float(2),
            tiempo_vuelo float(4),
            altura_maxima float(4),
            ultima_x float(2),
            ultima_y float(2),
            id_cliente int
    );""",
    """CREATE TABLE IF NOT EXISTS dispersion (
            id_cliente int,
            dispersion float(4),
            fecha_hora TIMESTAMP
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

xlist = []
ylist = []
zlist = []
dispersion = []

# obtengo una lista de colores del archivo de configuracion.
color = config["color"]
# color = ['red', 'green', 'blue', 'yellow',
#          'black', 'gray', 'pink', 'purple', 'orange']


def calcular_puntos(tiempo, tick, vz, vx, vy, x, y, z,
                    zviento, wind_duration, rx, ry,
                    duracion, ax, dot_color, vi, a, b, wind,
                    wind_angle, client_number,
                    cursor, hmax, cs):
    while True:
        tiempo = tiempo + tick
        vz = celery_calc.vz_variable.delay(vz, tick).get()
        x = celery_calc.pos_x.delay(x, vx, tick).get()
        y = celery_calc.pos_y.delay(y, vy, tick).get()
        z = celery_calc.pos_z.delay(z, vz, tick).get()
        if z <= 0:
            xlist.append(x)
            ylist.append(y)
            zlist.append(z)
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
        velocidad_inicial, angulo_salida, angulo_desviacion,
        velocidad_viento, angulo_viento, duracion_viento,
        tiempo_vuelo, altura_maxima, ultima_x, ultima_y,
        id_cliente
        ) VALUES (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )"""
    valores_insertar = (vi, a, b, wind, wind_angle,
                        wind_duration, tiempo, hmax, x, y, client_number)
    cursor.execute(query, valores_insertar)


def plot(vi, a, b, wind, wind_angle, dot_color, ax, wind_duration,
         cs, client_number, cursor):

    # calculos de componentes del vector velocidad
    velx = celery_calc.vel_x.delay(vi, a, b)
    vely = celery_calc.vel_y.delay(vi, a, b)
    velz = celery_calc.vel_z.delay(vi, a)

    # calculo de la altura del viento
    zviento = celery_calc.altura_viento.delay(velz.get())
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
                    cursor, hmax, cs)


def mp(clientsocket, client_number):

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
    cantidad = int(clientsocket.recv(1024).decode())
    vi = int(clientsocket.recv(1024).decode())
    a = int(clientsocket.recv(1024).decode())
    b = int(clientsocket.recv(1024).decode())
    while True:
        i += 1
        if i == cantidad:
            break
        wind = rnd.randint(0, 10)
        wind_angle = rnd.randint(0, 360)
        wind_duration = rnd.uniform(0, 1)
        data = f"""
(Simulacion {i+1}) Valores del viento:\n\tVelocidad = {wind} m/s
\tAngulo = {wind_angle}\n\tDuracion = {wind_duration}
"""
        clientsocket.send(data.encode())
        dot_color = color[rnd.randint(0, 8)]
        plot(vi, a, b, wind, wind_angle, dot_color,
             ax, wind_duration, clientsocket, client_number,
             cursor)
    plt.show()
    # print(dispersion)
    mayor = 0
    j = 1
    for i in range(len(dispersion)):
        for j in range(len(dispersion)):
            l = celery_calc.disp.delay(dispersion, i, j).get()
            # l = math.sqrt(((dispersion[j][0]-dispersion[i][0])
            #               ** 2) + ((dispersion[j][1]-dispersion[i][1])**2))
            #print(f'Distancia: {l}')
            if l > mayor:
                mayor = l
        j = + 1
    # print(f'Mayor distancia entre puntos = {mayor}')
    query = """ INSERT INTO dispersion (
        id_cliente, dispersion, fecha_hora
        ) VALUES (
            %s,%s,%s
        )"""
    valores_insertar = (client_number, mayor, str(datetime.now()))
    cursor.execute(query, valores_insertar)
    myConnection.commit()
    myConnection.close()
    msg = f"Simulacion terminada.\nDistancia maxima entre puntos finales = {mayor} m"
    clientsocket.send(msg.encode())
    time.sleep(0.1)
    exit_signal = "exit"
    clientsocket.send(exit_signal.encode())


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
        # inicio un proceso de manera concurrente
        p = multiprocessing.Process(
            target=mp, args=(clientsocket, client_number))
        p.start()


if __name__ == "__main__":
    multiP()
