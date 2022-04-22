from multiprocessing import Process
from calendar import c
from cv2 import line
import matplotlib.pyplot as plt
import numpy as np
import csv
from mpl_toolkits.mplot3d import axes3d
import random as rnd

def func1():
    xdata = []
    ydata = []
    zdata = []

    vi = rnd.randint(20, 30)
    anga = rnd.randint(30, 60)
    angb = rnd.randint(30, 60)
    vx = vi*np.cos(np.radians(anga))*np.cos(np.radians(angb)) # calculo de la velocidad inicial en x
    vy = vi*np.cos(np.radians(anga))*np.sin(np.radians(angb)) # calculo de la velocidad inicial en y
    vz = vi*np.sin(np.radians(anga)) # calculo de la velocidad inicial en z

    tick = 0.1

    for i in np.arange(0,5,tick):
        with open('datos.csv', 'a', newline='') as file:
            x = vx*i # x = vx*t
            y = vy*i
            z = vz*i-1/2*9.8*i**2
            if z < 0:
                print('termino')
                break
            xdata.append(x) 
            ydata.append(y)
            zdata.append(z)
            ax.scatter(x, y, z, c='g', marker='o')
            plt.draw()
            plt.pause(0.1)


if __name__ == '__main__':

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    # vi = int(input("Ingrese la velocidad inicial: ")) # velocidad inicial
    # anga = int(input("Ingrese el angulo de salida: ")) # angulo de salida en x
    # angb = int(input("Ingrese el angulo de desviacion: "))
    # vx = vi*np.cos(np.radians(anga))*np.cos(np.radians(angb)) # calculo de la velocidad inicial en x
    # vy = vi*np.cos(np.radians(anga))*np.sin(np.radians(angb)) # calculo de la velocidad inicial en y
    # vz = vi*np.sin(np.radians(anga))

    # vi2 = int(input("Ingrese la velocidad inicial: ")) # velocidad inicial
    # anga2 = int(input("Ingrese el angulo de salida: ")) # angulo de salida en x
    # angb2 = int(input("Ingrese el angulo de desviacion: "))
    # vx2 = vi2*np.cos(np.radians(anga2))*np.cos(np.radians(angb2)) # calculo de la velocidad inicial en x
    # vy2 = vi2*np.cos(np.radians(anga2))*np.sin(np.radians(angb2)) # calculo de la velocidad inicial en y
    # vz2 = vi2*np.sin(np.radians(anga2))

    p1 = Process(target=func1)
    p1.start()
    # p2 = Process(target=func1)
    # p2.start()
    p1.join()
    # p2.join()
    plt.show()