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

color = ['red', 'green', 'blue', 'yellow', 'black', 'gray', 'pink', 'purple', 'orange']

def plot(vi, a, b, wind, wind_angle, dot_color, ax):

    # calculos de componentes del vector velocidad
    velx = vi*np.cos(np.radians(a))*np.cos(np.radians(b))
    vely = vi*np.cos(np.radians(a))*np.sin(np.radians(b))
    velz = vi*np.sin(np.radians(a))
    # calculo de la altura del viento
    zviento = ((velz**2)/(2*9.8))*2/3
    # tick de tiempo
    tick = 0.05
    # calculos de componentes del vector velocidad del viento
    wx = wind*np.cos(np.radians(wind_angle))
    wy = wind*np.sin(np.radians(wind_angle))
    # calculos de componentes del vector resultante
    rx = velx + wx
    ry = vely + wy

    x=0
    y=0
    z=0
    vz = velz
    vx = velx
    vy = vely

    tiempo = 0

    while True:
        tiempo = tiempo + tick
        vz = vz - 9.8 * tick
        x = x + vx*tick
        y = y + vy*tick
        z = z + (vz*tick)-(1/2)*(9.8)*(tick**2)
        if z > zviento:
            vx = rx
            vy = ry
        if z <=0:
            xlist.append(x)
            ylist.append(y)
            zlist.append(z)
            break
        ax.scatter(x, y, z, c=dot_color, marker='o')
        # fig.canvas.draw()
        # fig.canvas.flush_events()
        plt.draw()
        plt.pause(0.0001)

    plt.show()


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
        dot_color = color[rnd.randint(0, 8)]
        plot(vi, a, b, wind, wind_angle, dot_color, ax)
        # wind_duration = int(clientsocket.recv(1024).decode())
    plt.show()


def multiP():
    client_number = -1
    while True:
        clientsocket, address = serversocket.accept()
        print("Got a connection from %s" % str(address))
        client_number += 1
        print(f'Client number: {client_number}')
        # wind_duration = int(clientsocket.recv(1024).decode())
        p = multiprocessing.Process(target=mp, args=(clientsocket, client_number))
        p.start()

if __name__ == "__main__":
    multiP()