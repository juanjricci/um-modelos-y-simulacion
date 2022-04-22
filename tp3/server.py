#!/usr/bin/python3
import socket
import argparse
import celery_calc
import matplotlib.pyplot as plt
import numpy as np
import csv
from mpl_toolkits.mplot3d import axes3d
import random as rnd

# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
"""
    socket.AF_INET -> sockets tcp/ip
    socket.AF_UNIX -> sockets Unix (archivos en disco, similar a FIFO/named pipes)
    socket.SOCK_STREAM -> socket tcp, orientado a la conexion (flujo de datos)
    socket.SOCK_DGRAM -> socket udp, datagrama de usuario (no orientado a la conexion)
"""
# get local machine name
parser = argparse.ArgumentParser(description="Calculadora")
parser.add_argument('-H', '--host', help='IP del host', required=True)
parser.add_argument('-p', '--port', type=int, help='Puerto de conexion', required=True)
args = parser.parse_args()

host = args.host
port = args.port

serversocket.bind((host, port))
serversocket.listen(2)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

xdata = []
ydata = []
zdata = []

while True:
    # establish a connection
    print("Esperando conexiones remotas (accept)")
    clientsocket, addr = serversocket.accept()
    print("Got a connection from %s" % str(addr))

    # recibe datos del cliente
    vi = int(clientsocket.recv(1024).decode())
    a = int(clientsocket.recv(1024).decode())
    b = int(clientsocket.recv(1024).decode())
    wind = int(clientsocket.recv(1024).decode())
    wind_angle = int(clientsocket.recv(1024).decode())
    wind_duration = int(clientsocket.recv(1024).decode())

    # calculos de componentes del vector velocidad
    vx = celery_calc.vel_x.delay(vi, a, b)
    vy = celery_calc.vel_y.delay(vi, a, b)
    vz = celery_calc.vel_z.delay(vi, a, b)

    print('Vector velocidad')
    print(vx.get())
    print(vy.get())
    print(vz.get())

    # calculo de la altura del viento
    zviento = celery_calc.altura_viento.delay(vz.get())

    print('Altura del viento')
    print(zviento.get())

    # calculos de componentes del vector velocidad del viento
    wx = celery_calc.wind_x.delay(wind, wind_angle)
    wy = celery_calc.wind_y.delay(wind, wind_angle)

    print('Vector viento')
    print(wx.get())
    print(wy.get())

    # calculos de componentes del vector resultante
    rx = celery_calc.res_x.delay(vx.get(), wx.get())
    ry = celery_calc.res_y.delay(vy.get(), wy.get())

    print('Vector resultante')
    print(rx.get())
    print(ry.get())

    print(f'N: {a}')
    print(f'M: {b}')
    print(f'Op: {vi}')

    color = ['g', 'r', 'b']
    color_pto = color[rnd.randint(0,2)]

    tick = 0.05

    x=0
    y=0
    z=0

    vz = vz.get()
    vx = vx.get()
    vy = vy.get()

    while True:
        vz = vz - 9.8 * tick
        x = celery_calc.pos_x.delay(x, vx, tick).get()
        y = celery_calc.pos_y.delay(y, vy, tick).get()
        z = celery_calc.pos_z.delay(z, vz, tick).get()
        if z > zviento.get():
            vx = rx.get()
            vy = ry.get()
            # x = x + vx * tick
            # y = y + vy * tick
        if z <=0:
            print("Cerrando conexion...")
            clientsocket.close()
            break
        ax.scatter(x, y, z, c='r', marker='o')
        plt.draw()
        plt.pause(0.001)

    plt.pause(1)