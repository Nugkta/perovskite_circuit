# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 17:13:26 2022

@author: pokey

For calculating the impedance of the equivelent circuit of the perovsite.

Might also give the separate current for the ionic and electronic part.




"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
#%%
q = 1.6e-19     #charge of electron
k = 1.38e-23    #boltzmann constant
T = 300     #room temperature


def Zcap(C , w):    #the impedance of a capacitor
    return 1/(1j * w * C)


#define the circuit of an equivalent circuit of a pervskite device
#required parameters are
#C_a,b,c,g: the capacitors in the circuit. See Onenote
#J_s: the saturation current of the transistor
#n: the ideality factor the transistor
#R_i: the ionic resistence
#V: the background voltage
#w: the frequency of the perturbation
#


def find_imp(w, C_a, C_b, R_i, C_g, C_c, J_s, n,  q_ini, V):  
    q_init = q_init 
    F = lambda t, Q: (V - Q/C_a - Q/C_b - Q/C_c)/R_i      #the ODE of the ionic branch
    #now solve for Q
    t_eval = np.arange(0, 5, 0.1)                      #times at which store in solution
    sol = solve_ivp(F, [0, 5], [q_init], t_eval=t_eval)     #approximate the solution in interval [0, 10], initial value of q
   #v1 = V - sol.y[0][-1]/C_a  #the voltage connecting to thetransistor
    v1 = 2
    J1 = J_s*(np.e**(q*(v1)/(n*k*T)) - np.e**(q*(v1 - V)/(n*k*T))) #finding J_1by using the property of thransistor
    Z_elct = 1/(J_s*(q/(k*T))*J1)   #finding the impedance of the electronic branch by differentiating dJ/dv
    Z_d = 1 / (1/Zcap(C_g,w) + 1/R_i)
    Z_ion = (Zcap(C_a,w) + Zcap(C_b,w) + Zcap(C_c,w) + Z_d)
    Z_tot = 1 / (1/Z_ion + 1/ Z_elct)
    return Z_tot



def find_implist(w_h, w_l,  C_a, C_b, R_i, C_g, C_c, J_s, n, q_init, V):
    wlist = np.arange(w_h, w_l, 1e-3)        #first resistence, second resistance, capacitance, type of plot(Nyquist or freqency)
    zrlist = []                                 #reference Note section 1
    zilist = []
    fzlist = []
    n=0                                 #the y axis of the Bode spectrum (the effective capacitance)
    for w in wlist:
        print(n)
        n+=1
        z = find_imp(w, C_a, C_b, R_i, C_g, C_c, J_s, n, V, q_init)
        zrlist.append(z.real)
        zilist.append(-z.imag)                    # use positive zimag to keep image in first quadrant
        fzlist.append((1/z).imag / w)           #fzlist is the effective capacitance term in the Bode plot y axis
    return np.array(wlist), np.array(zrlist), np.array(zilist), fzlist


#%%
#a, b, c, d= find_implist(1e-4, 10., 1., 1., 1., 1., 1., 1., 1., 1., 0)  

a, b, c, d= find_implist(0.001, 10, 10,10,4,4,10, 1,1,1,1)
print(a)




plt.plot(b,c,'.')
plt.title('Nyquist plot')
plt.xlabel('z_real')
plt.ylabel('y_real')

#%%
plt.plot(a,b,'.')
plt.plot(a,c,'.')
plt.xscale('log')
plt.legend(['z_real','z_imag'])
plt.xlabel('frequency')
plt.ylabel('magnitude of z')





#%%
#b = find_imp(10., 1., 1., 1., 1., 1., 1., 1., 1., 0)
#b = find_imp(1e-4, 1e-4,1e-4,4,4,1e-4,1e-4, 1,5,1)

wlist, zrlist, zilist, fzlist = a, b, c, d

#%% the previous steps generated set of data in wlist zilist and zrlist 
def func_imp(w, C_a, C_b, R_i, C_g, C_c, J_s, n,  q_init,V):                   #the funtion used in the curve fit(only to return a stacked real/imaginary part)
    z = find_imp(w, C_a, C_b, R_i, C_g, C_c, J_s, n, V, q_init)
    return np.hstack([z.real, z.imag])

def fit(wlist, zrlist, zilist, Vb):                          #returns the fitting parameters 
    Zlist = np.hstack([zrlist, -zilist])
    popt, pcov = curve_fit(lambda w,  C_a, C_b, R_i, C_g, C_c, J_s, n, q_init: func_imp(w, C_a, C_b, R_i, C_g, C_c, J_s, n, Vb, q_init) , wlist, Zlist, p0 = [1, 10,10,4,4,10, 1,1], maxfev = 10000)
    return popt, pcov

#def plot_fit(wlist, popt, zrlist, zilist): 
#    zfit = func_imp(wlist, *popt, find_imp)
#    zfit_r = zfit[0: len(wlist)]
#    zfit_i = zfit[len(wlist): 2 * len(wlist)]
#    fig = plt.figure()
#    plt.subplot((221))                          #z_real vs. freq
#    plt.xscale('log')
#    plt.plot(wlist, zrlist,'.')
#    plt.plot(wlist, zfit_r,'r--')
#    plt.title("Z_real vs. freq")
#    plt.subplot((222))                      #z_image vs. freq
#    plt.xscale('log')
#    plt.plot(wlist, zilist,'.')
#    plt.plot(wlist, -zfit_i,'r--')      #negative the fitted z_imag for Nyquist plot
#    plt.title("Z_imag vs. freq")
#    fig.add_subplot(2, 2, (3, 4))           #z_real vs. z_imag
#    plt.plot(zrlist,zilist,'.')
#    plt.plot(zfit_r, -zfit_i,'r--')
#    plt.title("Nyquist ")
#    
#
#def main(wlist, zrlist, zilist, vb):
#    popt, pcov = fit(wlist, zrlist, zilist,vb)
#    plot_fit(wlist, popt, zrlist, zilist)
#    print('the fit parameters are', *popt)
#    return popt, pcov

popt, pcov = fit(wlist, zrlist, zilist, 2)
zfit = func_imp(wlist, 1., 10., 10.,  4.,  4., 10.,  1.,  1.,  2)
zfit_r = zfit[0: len(wlist)]
plt.plot(wlist, zrlist,'.')
plt.plot(wlist, zfit_r,'r--')


































