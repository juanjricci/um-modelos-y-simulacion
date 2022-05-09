#!/usr/bin/python3

import socket
import argparse
import time
import random as rnd

# parseo de argumentos
parser = argparse.ArgumentParser(description="Calculadora")
# parser.add_argument('-H', '--host', help='IP del host', required=True)
# parser.add_argument('-p', '--port', type=int, help='Puerto de conexion', required=True)
parser.add_argument('-s', '--sim', type=int, help='Cantidad de simulaciones', required=True)
parser.add_argument('-v', '--vi', type=int, help='Velocidad inicial', required=True)
parser.add_argument('-a', type=int, help='Angulo de salida', required=True)
parser.add_argument('-b', type=int, help='Angulo de desviacion', required=True)
args = parser.parse_args()

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
print(s)

# get address
host = socket.gethostname()
port = 1234

print("Haciendo el connect")
# connection to hostname on the port.
s.connect((host, port))   
print("Handshake realizado con exito!")

cant = args.sim

vi = args.vi
a = args.a
b = args.b
# vi = int(input('Ingrese la velocidad de salida: '))
# a = int(input('Ingrese el angulo de salida (alfa): '))
# b = int(input('Ingrese el angulo de desviacion (beta): '))
time.sleep(0.5)

print(f'Cantidad de simulaciones = {cant}')
s.send(str(cant).encode())

print(f'Velocidad inicial = {vi} m/s')
s.send(str(vi).encode())
time.sleep(0.5)
print(f'Angulo de salida = {a}º')
s.send(str(a).encode())
time.sleep(0.5)
print(f'Angulo de desviacion = {b}º')
s.send(str(b).encode())
time.sleep(0.5)

# msg = s.recv(1024)
# print(f'Tiempo de vuelo = {msg.decode()}')

time.sleep(10)
s.close()
print("Cerrando conexion")