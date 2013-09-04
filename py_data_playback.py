# -*- coding: utf-8 -*-
"""
Created on Fri Aug 09 18:27:06 2013

@author: jh4209
"""

from nidaqmx import *
import time
import numpy
import scipy.io as sio
import threading
import sys
#import matplotlib.pyplot as pylab


#=======================================================        

class AO_threading(threading.Thread):
    def __init__(self,t,stim):
        threading.Thread.__init__( self )

#        self.sampling_time = 10      #... second
        #self.w = w
        self.t = t
#        stim=stim_gen(w=self.w, t=self.t, seq=1)
        #self.stim=stim
        self.AO_data = stim #self.stim['data']     # <<=== stimulus loading ===
        self.AO_rate = 20000        
    
    def run(self):
#        print "Stimulation running... at %d deg/sec " % (self.w)
#        rep = int(self.sampling_time / (tLmt*2*5000+1))
#        for i in range(rep):
        AO_task = AnalogOutputTask()
        AO_task.create_voltage_channel('Dev6/ao0:1', min_val=-10.0, max_val=10.0)
        AO_task.configure_timing_sample_clock(rate = self.AO_rate) 
        AO_task.set_regeneration(1)
        AO_task.write(self.AO_data, auto_start=False, layout = 'group_by_channel')
        AO_task.start()
#            print "Stimulation repetition: %d / %d" %((i+1),rep)
        time.sleep(self.t+1)   #tLmt*2*5000+1)


#=======================================================
#=======================================================
if __name__ == '__main__':
    
    
   
    matfile = 'D:\Jiaqi\data_2013-08-30\Data_3Ch_[2013-08-30_21-35-41]_TOP9_60degHz'
    print 'Loading...'
    print matfile
    
    matdata = sio.loadmat(matfile)
    data = matdata.get('vect'); del matdata;

    output = numpy.delete(data,2,0)
    output = numpy.reshape(output, numpy.size(output) ) #(1,-1)) #
#    output = output.T
    
#    output = numpy.tile([1,0],200000)

        
    AO = AO_threading(30,output)

    print "Replaying... " 
    #print matfile

    AO.start()

    while AO.is_alive():
        pass


    print 'Done.'
