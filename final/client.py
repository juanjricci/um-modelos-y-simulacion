#!/usr/bin/python3

import socket
import argparse
import time
import random as rnd
import json


# parseo de argumentos
parser = argparse.ArgumentParser(description="Calculadora")
parser.add_argument('--config', type=str, help='Ruta al archivo de configuracion', required=True)
args = parser.parse_args()

with open(args.config, 'r') as f:
    config = json.load(f)

cant = config["sim"]
vi = config["vi"]
a = config["a"]
b = config["b"]

print("Los valores por defecto seran:")
print(f"Cantidad de simulaciones = {cant}")
print(f"Velocidad inicial = {vi}")
print(f"Angulo de salida = {a}")
print(f"Angulo de desviacion = {b}")
mod = input("Desea modificarlos? [Y/N]: ")
if mod == 'Y' or mod == 'y':
    cant = input('Ingrese la cantidad de simulaciones deseada: ')
    vi = input('Ingrese la velocidad inicial: ')
    a = input('Ingrese el angulo de salida: ')
    b = input('Ingrese el angulo de desviacion: ')
else:
    pass

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
print(s)

# get address
host = config["host"]
port = config["port"]
# host = socket.gethostname()
# port = 1234

print("Haciendo el connect")
# connection to hostname on the port.
s.connect((host, port))   
print("Handshake realizado con exito!")

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

while True:
    data = s.recv(1000)
    if data.decode() == "exit":
        break
    print(data.decode())
#print(msg.decode())
# print(f'Tiempo de vuelo = {msg.decode()}')

#time.sleep(10)
s.close()
print("Cerrando conexion")