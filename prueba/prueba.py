from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np
import socket
import multiprocessing
import celery_calc
from mpl_toolkits.mplot3d import axes3d


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = socket.gethostname()
port = 1234

serversocket.bind((host, port))
serversocket.listen(2)

xlist = []
ylist = []
zlist = []


def plot(vi, a, b, wind, wind_angle, cs, client_number):

    # declaracion de la figura y sus ejes
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    # calculos de componentes del vector velocidad
    velx = celery_calc.vel_x.delay(vi, a, b)
    vely = celery_calc.vel_y.delay(vi, a, b)
    velz = celery_calc.vel_z.delay(vi, a, b)
    # calculo de la altura del viento
    zviento = celery_calc.altura_viento.delay(velz.get())
    # tick de tiempo
    tick = 0.05
    # calculos de componentes del vector velocidad del viento
    wx = celery_calc.wind_x.delay(wind, wind_angle)
    wy = celery_calc.wind_y.delay(wind, wind_angle)
    # calculos de componentes del vector resultante
    rx = celery_calc.res_x.delay(velx.get(), wx.get())
    ry = celery_calc.res_y.delay(vely.get(), wy.get())

    x=0
    y=0
    z=0
    vz = velz.get()
    vx = velx.get()
    vy = vely.get()

    tiempo = 0

    while True:
        tiempo = tiempo + tick
        vz = vz - 9.8 * tick
        x = celery_calc.pos_x.delay(x, vx, tick).get()
        y = celery_calc.pos_y.delay(y, vy, tick).get()
        z = celery_calc.pos_z.delay(z, vz, tick).get()
        if z > zviento.get():
            vx = rx.get()
            vy = ry.get()
        if z <=0:
            xlist.append(x)
            ylist.append(y)
            zlist.append(z)
            msg = f"Tiempo de vuelo = {tiempo}"
            cs.send(msg.encode())
            # print("Cerrando conexion...")
            cs.close()
            break
        ax.scatter(x, y, z, c='r', marker='o')
        plt.draw()
        plt.pause(0.001)

    plt.show()


def multiP():
    client_number = -1
    while True:
        clientsocket, address = serversocket.accept()
        print("Got a connection from %s" % str(address))
        client_number += 1
        print(f'Client number: {client_number}')
        vi = int(clientsocket.recv(1024).decode())
        a = int(clientsocket.recv(1024).decode())
        b = int(clientsocket.recv(1024).decode())
        wind = int(clientsocket.recv(1024).decode())
        wind_angle = int(clientsocket.recv(1024).decode())
        # wind_duration = int(clientsocket.recv(1024).decode())
        p = multiprocessing.Process(target=plot, args=(vi, a, b, wind, wind_angle, clientsocket, client_number))
        p.start()

if __name__ == "__main__":
    multiP()