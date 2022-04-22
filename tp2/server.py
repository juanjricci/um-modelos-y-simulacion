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

    vi = int(clientsocket.recv(1024).decode())
    # if vi == 0:
    #     break
    a = int(clientsocket.recv(1024).decode())
    b = int(clientsocket.recv(1024).decode())

    vx = vi*np.cos(np.radians(a))*np.cos(np.radians(b)) # calculo de la velocidad inicial en x
    vy = vi*np.cos(np.radians(a))*np.sin(np.radians(b)) # calculo de la velocidad inicial en y
    vz = vi*np.sin(np.radians(a)) # calculo de la velocidad inicial en z

    print(f'N: {a}')
    print(f'M: {b}')
    print(f'Op: {vi}')

    color = ['g', 'r', 'b']
    color_pto = color[rnd.randint(0,2)]

    tick = 0.1

    for i in np.arange(0,5,tick):
        x = celery_calc.pos_x.delay(vx, i)
        y = celery_calc.pos_y.delay(vy, i)
        z = celery_calc.pos_z.delay(vz, i)
        if z.get() < 0:
            break
        xdata.append(x.get()) 
        ydata.append(y.get())
        zdata.append(z.get())
        ax.scatter(x.get(), y.get(), z.get(), c=color_pto, marker='o')
        plt.draw()
        plt.pause(0.1)

    print("Cerrando conexion...")
    clientsocket.close()
