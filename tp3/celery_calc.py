import numpy as np
"""
Funciones matematicas
"""

from celery_calc_config import app

# CALCULOS DE LAS COMPONENTES DE LAS VELOCIDADES

@app.task
def vel_x(vi, a, b): # calculo de la velocidad en x
    return vi*np.cos(np.radians(a))*np.cos(np.radians(b))

@app.task
def vel_y(vi, a, b): # calculo de la velocidad en y
    return vi*np.cos(np.radians(a))*np.sin(np.radians(b))

@app.task
def vel_z(vi, a, b): # calculo de la velocidad en z
    return vi*np.sin(np.radians(a))

# CALCULOS DEL VIENTO

@app.task
def wind_x(wind, wind_angle): # calculo de la velocidad del viento en x
    return wind*np.cos(np.radians(wind_angle))

@app.task
def wind_y(wind, wind_angle): # calculo de la velocidad del viento en y
    return wind*np.sin(np.radians(wind_angle))
    

# CALCULO DE 2/3 DE LA ALTURA MAXIMA

@app.task
def altura_viento(vz):
    return ((vz**2)/(2*9.8))*2/3 # zmax = (vz^2)/2*g

# CALCULOS DE LAS POSICIONES (PUNTOS EN X, Y, Z)

@app.task
def pos_x(vx, i): # calculo de la posicion en x
    return vx*i # x = vx*t

@app.task
def pos_y(vy, i): # calculo de la posicion en y
    return vy*i # x = vx*t

@app.task
def pos_z(vz, i): # calculo de la posicion en z
    return vz*i-1/2*9.8*i**2 # x = vx*t

# CALCULOS DE LAS COMPONENTES DEL VECTOR RESULTANTE

@app.task
def res_x(vx, wx):
    return vx + wx

@app.task
def res_y(vy, wy):
    return vy + wy

@app.task
def pos_res_x(x, rx, i):
    return x + rx*i

@app.task
def pos_res_y(y, ry, i):
    return y + ry*i

        
