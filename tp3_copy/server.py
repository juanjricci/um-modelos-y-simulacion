#!/usr/bin/python3
import socket
import argparse
import celery_calc
import matplotlib.pyplot as plt
import numpy as np
import csv
from mpl_toolkits.mplot3d import axes3d
import random as rnd
import _thread

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

threadCount = 0

# xdata = []
# ydata = []
# zdata = []

# client_count = -1
# client_color = ['g', 'r', 'b', 'y']

def threaded_client(connection):

    #client_count = client_count + 1
    #color = client_color[client_count]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    # recibe datos del cliente
    vi = int(connection.recv(1024).decode())
    a = int(connection.recv(1024).decode())
    b = int(connection.recv(1024).decode())
    wind = int(connection.recv(1024).decode())
    wind_angle = int(connection.recv(1024).decode())
    wind_duration = int(connection.recv(1024).decode())

    # calculos de componentes del vector velocidad
    velx = celery_calc.vel_x.delay(vi, a, b)
    vely = celery_calc.vel_y.delay(vi, a, b)
    velz = celery_calc.vel_z.delay(vi, a, b)

    print('Vector velocidad')
    print(velx.get())
    print(vely.get())
    print(velz.get())

    # calculo de la altura del viento
    zviento = celery_calc.altura_viento.delay(velz.get())

    print('Altura del viento')
    print(zviento.get())

    tick = 0.05

    # calculos de componentes del vector velocidad del viento
    wx = celery_calc.wind_x.delay(wind, wind_angle)
    wy = celery_calc.wind_y.delay(wind, wind_angle)

    print('Vector viento')
    print(wx.get())
    print(wy.get())

    # calculos de componentes del vector resultante
    rx = celery_calc.res_x.delay(velx.get(), wx.get())
    ry = celery_calc.res_y.delay(vely.get(), wy.get())

    print('Vector resultante')
    print(rx.get())
    print(ry.get())

    print(f'N: {a}')
    print(f'M: {b}')
    print(f'Op: {vi}')

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
            msg = f"Tiempo de vuelo = {tiempo}"
            connection.send(msg.encode())
            print("Cerrando conexion...")
            connection.close()
            break
        ax.scatter(x, y, z, c='r', marker='o')
        plt.draw()
        plt.pause(0.001)

while True:

    clientsocket, address = serversocket.accept()
    print("Got a connection from %s" % str(address))
    _thread.start_new_thread(threaded_client, (clientsocket, ))
    threadCount += 1
    print('Thread Number: ' + str(threadCount))

    #plt.pause(5)