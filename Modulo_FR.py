import pydicom as pcm
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.odr import ODR, Model, RealData
from sklearn.metrics import r2_score




def Ajuste_ODR(x,y,sdx,sdy, tipo = 'lineal',xlbel = 'MPV',ylbel = 'Kerma'):
    '''
    Esta funcion calcula el ajuste ODR (lineal) de datos x y y con sus respectivos desviaciones estandar
    '''

    odr_data = RealData(x = x, y = y, sx= sdx, sy =sdy)

    #Modelo del ODR en este caso debe de ser lineal o exponencial

    def lineal(B,x):
        return B[0]*x + B[1]
    
    def exponencial(B,x):
        return B[0]*np.exp(x)**B[1]
    ####Modelo

    if tipo == 'lineal':

        odr_model = Model(lineal)

    elif tipo == 'exponencial':
        odr_model = Model(exponencial)

    #Ajuste
    odr_fit = ODR(odr_data,odr_model, beta0= [1,1])
    out = odr_fit.run()
    
    param = out.beta
    incert = out.sd_beta

    m,b = param
    dm, db = incert
    x_fit = np.linspace(x[0],x[-1], 1000)
    y_fit = lineal(param,x_fit)

    y_pred = lineal(param,x)

    R2 = r2_score(y, y_pred)





    texto =( 
         r'$y = mx + b$' + '\n'
        + r'$m = ({:.3e} \pm {:.3e})$'.format(m, dm) + '\n'
        + r'$b = ({:.3e} \pm {:.3e})$'.format(b, db) + '\n'
        +r'$R^2 = ({:.3f}) $'.format(R2)
    )    

    plt.errorbar(
            x, y,
    xerr=sdx, yerr=sdy,
    fmt='o', color='crimson',
    ecolor='lightgray', elinewidth=1.5, capsize=3,
    label='Datos experimentales'
    )
    plt.plot(x_fit,y_fit, label = 'Ajuste',color = 'royalblue')
    plt.grid()
    plt.ylabel(ylbel)
    plt.xlabel(xlbel)
    plt.legend()
    plt.gca().text(
        0.05, 0.95, texto,
        transform=plt.gca().transAxes,
        fontsize=10,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
    )
    plt.tight_layout
    plt.title('Ajuste datos ')
    plt.show()
    
    return param, incert, R2

def ROI_calculadora(I,x,y,l = 100):
    '''
    
    '''
    x = int(x)
    y = int(y)
    half_l = int(l // 2)
    x_min = max(0, x - half_l)
    x_max = min(I.shape[0], x + half_l)
    y_min = max(0, y - half_l)
    y_max = min(I.shape[1], y + half_l)

    ROI = I[x_min:x_max, y_min:y_max]
    MPV = np.mean(ROI)
    sd_MPV = np.std(ROI)

    return MPV, sd_MPV

def centro(I):
    x,y = (I.shape[0] // 2, I.shape[1] // 2)
    return x, y


def Conversion_exponencial(P,B,A):
    termino = (P-B)/A
    return np.exp(termino)

def percentil(I, p= 99):
    '''
    Esta funcion calcula el percentil de una imagen I
    '''

    I = I.flatten()
    I = np.sort(I)
    low = np.percentile(I, p)
    high = np.percentile(I, 100 - p)
    return low, high
    

def ODR_adjust(x,y,sdx,sdy, tipo = 'lineal',xlbel = 'MPV',ylbel = 'Kerma'):
    '''
    Esta funcion calcula el ajuste ODR (lineal) de datos x y y con sus respectivos desviaciones estandar
    '''

    odr_data = RealData(x = x, y = y, sx= sdx, sy =sdy)

    #Modelo del ODR en este caso debe de ser lineal o exponencial

    def lineal(B,x):
        return B[0]*x + B[1]
    
    def exponencial(B,x):
        return B[0]*np.exp(x)**B[1]
    ####Modelo

    if tipo == 'lineal':

        odr_model = Model(lineal)

    elif tipo == 'exponencial':
        odr_model = Model(exponencial)

    #Ajuste
    odr_fit = ODR(odr_data,odr_model, beta0= [1,1])
    out = odr_fit.run()
    
    param = out.beta
    incert = out.sd_beta

    m,b = param
    dm, db = incert
    x_fit = np.linspace(x[0],x[-1], 1000)
    y_fit = lineal(param,x_fit)

    y_pred = lineal(param,x)

    R2 = r2_score(y, y_pred)

    return param, incert, R2    

