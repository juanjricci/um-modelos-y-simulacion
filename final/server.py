from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np
import celery_calc
from mpl_toolkits.mplot3d import axes3d
import random as rnd
import socket
import multiprocessing
import time


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = socket.gethostname()
port = 1234

serversocket.bind((host, port))
serversocket.listen(2)

xlist = []
ylist = []
zlist = []

color = ['red', 'green', 'blue', 'yellow',
         'black', 'gray', 'pink', 'purple', 'orange']


def calcular_puntos(tiempo, tick, vz, vx, vy, x, y, z,
                    zviento, wind_duration, rx, ry,
                    duracion, ax, dot_color):
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
            #print(xlist)
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
    print(f'Duracion del viento: {duracion}')


def plot(vi, a, b, wind, wind_angle, dot_color, ax, wind_duration, cs):

    # calculos de componentes del vector velocidad
    velx = celery_calc.vel_x.delay(vi, a, b)
    vely = celery_calc.vel_y.delay(vi, a, b)
    velz = celery_calc.vel_z.delay(vi, a)

    # calculo de la altura del viento
    zviento = celery_calc.altura_viento.delay(velz.get())

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
                    wind_duration, rx, ry, duracion, ax, dot_color)


def mp(clientsocket, client_number):
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
        dot_color = color[rnd.randint(0, 8)]
        plot(vi, a, b, wind, wind_angle, dot_color,
             ax, wind_duration, clientsocket)
    plt.show()


def multiP():
    client_number = -1
    while True:
        clientsocket, address = serversocket.accept()
        print("Got a connection from %s" % str(address))
        client_number += 1
        print(f'Client number: {client_number}')
        # wind_duration = int(clientsocket.recv(1024).decode())
        p = multiprocessing.Process(
            target=mp, args=(clientsocket, client_number))
        p.start()


if __name__ == "__main__":
    multiP()
