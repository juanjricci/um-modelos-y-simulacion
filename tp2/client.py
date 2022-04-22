#!/usr/bin/python3

import socket
import argparse
import time
import random as rnd

# parseo de argumentos
parser = argparse.ArgumentParser(description="Calculadora")
parser.add_argument('-H', '--host', help='IP del host', required=True)
parser.add_argument('-p', '--port', type=int, help='Puerto de conexion', required=True)
#parser.add_argument('-v', '--vi', type=int, help='Velocidad inicial', required=True)
#parser.add_argument('-a', type=int, help='Angulo de salida', required=True)
#parser.add_argument('-b', type=int, help='Angulo de desviacion', required=True)
args = parser.parse_args()

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
print(s)

# get address
host = args.host
port = args.port

print("Haciendo el connect")
# connection to hostname on the port.
s.connect((host, port))   
print("Handshake realizado con exito!")

vi = 25
a = 45
b = 45

# vv = rnd.randint(0,30) # velocidad del viento
# dv = rnd.uniform(0,1) # duracion del viento
# sv = rnd.randint(0, 360) # sentido del viento

print(f'Velocidad inicial = {vi} km/h')
s.send(str(vi).encode())
time.sleep(0.5)
print(f'Angulo de salida = {a}º')
s.send(str(a).encode())
time.sleep(0.5)
print(f'Angulo de desviacion = {b}º')
s.send(str(b).encode())
time.sleep(0.5)


s.close()
print("Cerrando conexion")