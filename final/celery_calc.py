import math
import numpy as np
"""
Funciones matematicas
"""

from celery_calc_config import app

# CALCULOS DE LAS COMPONENTES DE LAS VELOCIDADES
@app.task
def vel_x(vi, a, b):  # calculo de la velocidad en x
    return vi*np.cos(np.radians(a))*np.cos(np.radians(b))

@app.task
def vel_y(vi, a, b):  # calculo de la velocidad en y
    return vi*np.cos(np.radians(a))*np.sin(np.radians(b))

@app.task
def vel_z(vi, a):  # calculo de la velocidad en z
    return vi*np.sin(np.radians(a))

@app.task
def vz_variable(vz, tick):
    return vz - 9.8 * tick


# CALCULOS DEL VIENTO
@app.task
def wind_x(wind, wind_angle):  # calculo de la velocidad del viento en x
    return wind*np.cos(np.radians(wind_angle))

@app.task
def wind_y(wind, wind_angle):  # calculo de la velocidad del viento en y
    return wind*np.sin(np.radians(wind_angle))


# CALCULO DE 2/3 DE LA ALTURA MAXIMA
@app.task
def altura_viento(vz):
    return ((vz**2)/(2*9.8))*2/3  # zmax = (vz^2)/2*g


# CALCULOS DE LAS POSICIONES (PUNTOS EN X, Y, Z)
@app.task
def pos_x(x, vx, tick):  # calculo de la posicion en x
    return x + vx*tick

@app.task
def pos_y(y, vy, tick):  # calculo de la posicion en y
    return y + vy*tick

@app.task
def pos_z(z, vz, tick):  # calculo de la posicion en z
    return z + (vz*tick)-(1/2)*(9.8)*(tick**2)


# CALCULOS DE LAS COMPONENTES DEL VECTOR RESULTANTE
@app.task
def res_x(vx, wx):
    return vx + wx

@app.task
def res_y(vy, wy):
    return vy + wy


# CALCULO DE DISPERSION (MAYOR DISTANCIA ENTRE PUNTOS FINALES)
@app.task
def disp(dispersion, i, j):
    return math.sqrt(((dispersion[j][0]-dispersion[i][0]) ** 2) + ((dispersion[j][1]-dispersion[i][1])**2))
