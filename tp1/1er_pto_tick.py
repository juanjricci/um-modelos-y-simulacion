from cProfile import label
from sre_parse import CATEGORIES
from matplotlib import markers
import matplotlib.pyplot as plt
import numpy as np
import csv
# import time
 
xdata = []
ydata = []
 
plt.show()
plt.xlabel('x')
plt.ylabel('y')
plt.title('Trayectoria de una pelota de golf')
 
axes = plt.gca()
axes.set_xlim(0, 70)
axes.set_ylim(0, +50)
line, = axes.plot(xdata, ydata, 'r-o')
axes.grid(color='grey', linestyle='--', linewidth=1, alpha=0.5)

vi = int(input("Ingrese la velocidad inicial: ")) # velocidad inicial
angx = int(input("Ingrese el angulo de salida: ")) # angulo de salida en x
vx = vi*np.cos(np.radians(angx)) # calculo de la velocidad inicial en x
vy = vi*np.sin(np.radians(angx)) # calculo de la velocidad inicial en y

tick = 0.05

with open('datos.csv', 'w', newline='') as file: 
    writer = csv.writer(file)
    writer.writerow(["x", "y"])
for i in np.arange(0,5,tick):
    with open('datos.csv', 'a', newline='') as file:
        x = vx*i # x = vx*t
        y = 0+vy*i-1/2*9.8*i**2 # y = H + vy*t - 1/2*g* t^2
        if y < 0:
            print('termino')
            break
        xdata.append(x) 
        ydata.append(y) 
        writer = csv.writer(file) 
        writer.writerow([x, y])
        line.set_xdata(xdata)
        line.set_ydata(ydata)
        plt.draw()
        plt.pause(0.1)
        if i == 4:
            break
        #timesleep(0.1)

plt.show()