# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 21:29:41 2013

@author: jh4209
"""

#from nidaqmx import *
#import time
import numpy
import scipy.io as sio
#import threading
#import sys
import matplotlib.pyplot as pylab

""" Data loading """

#matfile = 'G:\[JH4209]\[JH][Recording]\Data_3Ch_BOT5_540degHz_[2013-01-29_15-29-48].mat'
matfile = 'H:\py_flylab\py_H1_calibration\Data_3Ch_CALI_30degHz_[2013-02-26_19-10-54].mat'
matdata = sio.loadmat(matfile)
data = matdata.get('vect'); del matdata;

Fs = 20000
Period = 10
t = numpy.arange(start=0, stop=Period, step=1.0/Fs,dtype=numpy.float64)


""" Data processing """
""" Spike train detection """

threshold = 2.5-0.25

spike_train = numpy.zeros(Fs*Period, dtype=numpy.uint)
for i in range(1,Fs*Period):
    if (data[0,i]>=threshold and data[0,i-1]<=threshold):
        spike_train[i] = 1
        

""" Firing rate calculation """




""" Data ploting """
fig = pylab.figure()
#pylab.plot(t,data[0,:],'b')
#pylab.plot(t,data[1,:],'r')
#pylab.plot(t,data[2,:],'k')

ax=pylab.subplot(2,1,1)
pylab.plot(t,data[0,:],'b',t,data[1,:],'r',t,data[2,:],'k')
pylab.axhspan(threshold,threshold,0, Fs*Period, color='g', alpha=0.5)

pylab.subplot(2,1,2, sharex=ax)
pylab.plot(t,spike_train,'k')
#pylab.plot(t,data[0,:],'b',t,data[1,:],'r',t,data[2,:],'k')
pylab.show()
