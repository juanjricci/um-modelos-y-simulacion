from calendar import c
from cv2 import line
import matplotlib.pyplot as plt
import numpy as np
import csv
from mpl_toolkits.mplot3d import axes3d
# import time
 
xdata = []
ydata = []
zdata = []

xdata2 = []
ydata2 = []
zdata2 = []

#ax = plt.axes(projection='3d')
#line, = ax.plot(xdata, ydata, zdata, 'r-o')
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

#ax.set_xlim(0, 70)
#ax.set_ylim(0, 70)
#ax.set_zlim(0, 70)

vi = int(input("Ingrese la velocidad inicial: ")) # velocidad inicial
anga = int(input("Ingrese el angulo de salida: ")) # angulo de salida en x
angb = int(input("Ingrese el angulo de desviacion: "))
vx = vi*np.cos(np.radians(anga))*np.cos(np.radians(angb)) # calculo de la velocidad inicial en x
vy = vi*np.cos(np.radians(anga))*np.sin(np.radians(angb)) # calculo de la velocidad inicial en y
vz = vi*np.sin(np.radians(anga))

vi2 = int(input("Ingrese la velocidad inicial: ")) # velocidad inicial
anga2 = int(input("Ingrese el angulo de salida: ")) # angulo de salida en x
angb2 = int(input("Ingrese el angulo de desviacion: "))
vx2 = vi2*np.cos(np.radians(anga2))*np.cos(np.radians(angb2)) # calculo de la velocidad inicial en x
vy2 = vi2*np.cos(np.radians(anga2))*np.sin(np.radians(angb2)) # calculo de la velocidad inicial en y
vz2 = vi2*np.sin(np.radians(anga2))

tick = 0.05

with open('datos.csv', 'w', newline='') as file: 
    writer = csv.writer(file)
    writer.writerow(["x", "y"])

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
        #line.set_xdata(xdata)
        #line.set_ydata(ydata)
        #line.set_zdata(zdata)
        ax.scatter(x, y, z, c='g', marker='o')
        plt.draw()
        plt.pause(0.01)

for i in np.arange(0,5,tick):
    with open('datos.csv', 'a', newline='') as file:
        x2 = vx2*i # x = vx*t
        y2 = vy2*i
        z2 = vz2*i-1/2*9.8*i**2
        if z2 < 0:
            print('termino')
            break
        xdata2.append(x2) 
        ydata2.append(y2)
        zdata2.append(z2)
        #line.set_xdata(xdata)
        #line.set_ydata(ydata)
        #line.set_zdata(zdata)
        ax.scatter(x2, y2, z2, c='r', marker='o')
        plt.draw()
        plt.pause(0.01)
        #if i == 4:
            #break
        #timesleep(0.1)

plt.show()