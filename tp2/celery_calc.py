import numpy as np
"""
Funciones matematicas
"""

from celery_calc_config import app

@app.task
def pos_x(vx, i): # calculo de la posicion en x
    return vx*i # x = vx*t

@app.task
def pos_y(vy, i): # calculo de la posicion en y
    return vy*i # x = vx*t

@app.task
def pos_z(vz, i): # calculo de la posicion en z
    return vz*i-1/2*9.8*i**2 # x = vx*t
        
