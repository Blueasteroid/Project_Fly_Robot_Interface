#Acq_IncClk.py
# This is a near-verbatim translation of the example program
# C:\Program Files\National Instruments\NI-DAQ\Examples\DAQmx ANSI C\Analog In\Measure Voltage\Acq-Int Clk\Acq-IntClk.c
import ctypes
import numpy
import scipy.io as sio
import time
import os

nidaq = ctypes.windll.nicaiu # load the DLL
##############################
# Setup some typedefs and constants
# to correspond with values in
# C:\Program Files\National Instruments\NI-DAQ\DAQmx ANSI C Dev\include\NIDAQmx.h
# the typedefs
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
# the constants
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_GroupByChannel = 0

##############################



def CHK(err):
    """a simple error checking routine"""
    if err < 0:
        buf_size = 100
        buf = ctypes.create_string_buffer('\000' * buf_size)
        nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
        raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))


# initialize variables
taskHandle = TaskHandle(0)

sampling_rate = 20000
sampling_time = 10      #... second
channel = 3

max_num_samples = sampling_rate * sampling_time * channel
data = numpy.zeros((max_num_samples,),dtype=numpy.float64)




# now, on with the program
CHK(nidaq.DAQmxCreateTask("",ctypes.byref(taskHandle)))
CHK(nidaq.DAQmxCreateAIVoltageChan(taskHandle,"Dev5/ai1:3","",
                                   DAQmx_Val_Cfg_Default,
                                   float64(-10.0),float64(10.0),
                                   DAQmx_Val_Volts,None))
CHK(nidaq.DAQmxCfgSampClkTiming(taskHandle,"",float64(20000.0),
                                DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,
                                uInt64(max_num_samples)));

print "Waiting for trigger... "     #... debug
os.system("pause")
#print "Data saving... "     #... debug

print "Recording... "     #... debug

CHK(nidaq.DAQmxStartTask(taskHandle))
read = int32()
CHK(nidaq.DAQmxReadAnalogF64(taskHandle,-1,float64(10.0),
                             DAQmx_Val_GroupByChannel,data.ctypes.data,
                             max_num_samples,ctypes.byref(read),None))

print "Acquired %d points"%(read.value)
if taskHandle.value != 0:
    nidaq.DAQmxStopTask(taskHandle)
    nidaq.DAQmxClearTask(taskHandle)
    
# print "End of program "
# print data

vect = numpy.zeros((3,), dtype=numpy.object)
vect[0]=data[0 : sampling_rate*sampling_time]
vect[1]=data[sampling_rate*sampling_time : sampling_rate*sampling_time*2]
vect[2]=data[sampling_rate*sampling_time*2 : max_num_samples]
#vect[1]=data[0.5*max_num_samples : max_num_samples]
#vect[1]=data[0.5*max_num_samples : max_num_samples]


# sio.savemat ('scipy_io_test.mat',{'vect':data})
sio.savemat ('Data_3Ch_SB_' + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '_[].mat',{'vect':vect})
print "Data saved! "    #... debug
# raw_input()
