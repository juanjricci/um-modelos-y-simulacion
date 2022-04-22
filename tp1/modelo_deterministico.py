from matplotlib.pylab import *
import matplotlib.pyplot as plt
import numpy as np
from math import *
import math

x = []
y = []

axes = plt.gca()
axes.set_xlim(0, 80)
axes.set_ylim(0, +50)
axes.grid(color='grey', linestyle='--', linewidth=1, alpha=0.5)
#line, = axes.plot(x, y)

vi = int(input("Ingrese la velocidad inicial: ")) # velocidad inicial
angx = int(input("Ingrese el angulo de salida: ")) # angulo de salida en x
vx = vi*np.cos(np.radians(angx)) # calculo de la velocidad inicial en x
vy = vi*np.sin(np.radians(angx)) # calculo de la velocidad inicial en y

for i in np.arange(0,5,0.05):
    x.append(vx*i) # x = vx*t
    y.append(0+vy*i-1/2*9.8*i**2) # y = H + vy*t - 1/2*g* t^2
    #if y[i] <= 0:
    #    y[i] = 0
    #    break

plt.plot(x, y, 'r-o')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Trayectoria de una pelota de golf')
plt.show()