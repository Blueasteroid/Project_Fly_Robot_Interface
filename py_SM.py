# Sine wave stimuli stepper motor driver script based on NI-USB-6215
# Jiaqi Huang, Imperial College London
# 23-Oct-2012
#

import ctypes
import numpy
import threading
import time

nidaq = ctypes.windll.nicaiu 

# ### Analog constant ###
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32

DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_ContSamps = 10123
DAQmx_Val_GroupByChannel = 0


# ### Digital constant ###
uint8 = ctypes.c_uint8
#uInt32 = ctypes.c_ulong
#uInt64 = ctypes.c_ulonglong
#float64 = ctypes.c_double
#TaskHandle = uInt32

DAQmx_Val_ChanForAllLines = 1
DAQmx_Val_GroupByChannel = 0


# ### Analog class ###
class WaveformThread( threading.Thread ):
    """
    This class performs the necessary initialization of the DAQ hardware and
    spawns a thread to handle playback of the signal.
    It takes as input arguments the waveform to play and the sample rate at which
    to play it.
    This will play an arbitrary-length waveform file.
    """
    def __init__( self, waveform0, waveform1, sampleRate ):
        self.running = True
        self.sampleRate = sampleRate
        self.periodLength = len( waveform0 )
        self.taskHandle = TaskHandle( 0 )
        self.data = numpy.zeros( ( self.periodLength *2, ), dtype=numpy.float64 )
        # convert waveform to a numpy array
        for i in range( self.periodLength ):
            self.data[ i ]                      = waveform0[ i ]
            self.data[ i+self.periodLength ]    = waveform1[ i ]
        # setup the DAQ hardware
        self.CHK(nidaq.DAQmxCreateTask("",
                          ctypes.byref( self.taskHandle )))
        
        self.CHK(nidaq.DAQmxCreateAOVoltageChan( self.taskHandle,
                                   "Dev2/ao0:1",
                                   "",
                                   float64(-10.0),
                                   float64(10.0),
                                   DAQmx_Val_Volts,
                                   None))

        
        self.CHK(nidaq.DAQmxCfgSampClkTiming( self.taskHandle,
                                "",
                                float64(self.sampleRate),
                                DAQmx_Val_Rising,
                                DAQmx_Val_FiniteSamps,
                                uInt64(self.periodLength)));
        self.CHK(nidaq.DAQmxWriteAnalogF64( self.taskHandle,
                              int32(self.periodLength),
                              0,
                              float64(-1),
                              DAQmx_Val_GroupByChannel,
                              self.data.ctypes.data,
                              None,
                              None))
        threading.Thread.__init__( self )
    def CHK( self, err ):
        """a simple error checking routine"""
        if err < 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
            raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))
        if err > 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
            raise RuntimeError('nidaq generated warning %d: %s'%(err,repr(buf.value)))
    def run( self ):
        counter = 0
        self.CHK(nidaq.DAQmxStartTask( self.taskHandle ))
    def stop( self ):
        self.running = False
        nidaq.DAQmxStopTask( self.taskHandle )
        nidaq.DAQmxClearTask( self.taskHandle )


# ### Digital class ###
class Ports( object ):

    def __init__( self ):

        self.port1 = [0,0,0,0]
        self.port1data = numpy.zeros((4,), numpy.uint8 )
        self.taskHandle1 = TaskHandle( 1 )
        
        self.CHK(nidaq.DAQmxCreateTask("",
                          ctypes.byref( self.taskHandle1 )))
        
        self.CHK(nidaq.DAQmxCreateDOChan( self.taskHandle1,
                                   "Dev2/port1/line0:3",
                                   "",
                                   DAQmx_Val_ChanForAllLines))
       
        self.run(self.taskHandle1)
        
        # Initialize digital ports
        self.update( port1 = self.port1) 
        
    def CHK( self, err ):
        """a simple error checking routine"""
        if err < 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
            raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))
        if err > 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
            raise RuntimeError('nidaq generated warning %d: %s'%(err,repr(buf.value)))
        
    def run( self, taskHandle ):
        self.CHK(nidaq.DAQmxStartTask( taskHandle ))
        
    def stop( self ):
        nidaq.DAQmxStopTask( self.taskHandle1 )
        nidaq.DAQmxClearTask( self.taskHandle1 )
        
    def update(self, port1 = [0,0,0,0]):
        if len(port1) != 4:
            raise ValueError('port1 argument must have 4 values')

        for i in range(len(port1)):
            self.port1data[i] = port1[i]
        self.CHK(nidaq.DAQmxWriteDigitalLines( self.taskHandle1,
                              1, 1, float64(10.0),
                              DAQmx_Val_GroupByChannel,
                              self.port1data.ctypes.data,
                              None,
                              None))





class DigitalOutThread( threading.Thread ):
    
    def __init__( self, freq ):

        self.DO = Ports()
        self.DO.update()
        self.freq=freq
        threading.Thread.__init__(self)
        
    def run( self ):

        self.DO.update(port1=[1,0,0,0])
        time.sleep((1.0/self.freq)*0.5)
        self.DO.update()
        time.sleep((1.0/self.freq)*0.5)
        
        self.DO.update(port1=[1,0,0,0])
        time.sleep(0.0001)
        self.DO.update()
#        time.sleep((1.0/self.freq)*0.5)
        
    def stop( self ):
        self.DO.stop()

# ######################################################################

def cos_pattern(AO_resolution, freq):
# Experiment spec: sinewave on angles of stepper motor:
# 60 degree amplitude (max), 15 Hz (max)
# from Karin and Holger 12-apr-2011 15:00:00

    step = 360.0/5000      #...step(/microstep) angle (degree)
    amp = 60       /2  #...sine wave amplitude (peak to peak degree)
#    freq = 1      #...sine wave frequency (Hz)

    Y = numpy.arange(0,amp,step)   
    X = (1/(2*numpy.pi*freq))*numpy.arcsin(Y/amp)

#    AO_resolution = 2.5e-6          # (us) resolution: 400k Hz maximum, the period of which is 2.5 us
#    AO_resolution = 5e-6          # (us) resolution: 200k Hz maximum, the period of which is 5 us
#    AO_resolution = 1e-4          # (us) resolution: 10k Hz maximum, the period of which is 100 us

    Xs = numpy.fix(X / AO_resolution )

    SM_sig = numpy.zeros(numpy.fix(Xs[numpy.size(Xs)-1])+1)
    for i in range(numpy.size(Xs)): SM_sig[Xs[i]]=1

    rev_SM_sig = numpy.zeros(numpy.fix(Xs[numpy.size(Xs)-1])+1)
    for i in range(numpy.size(SM_sig)): rev_SM_sig[i]=SM_sig[numpy.size(SM_sig)-1-i]

#    duration = 2 * X[numpy.size(X)-1]    # (second) duration of the signal train

    wavelet = 5 * numpy.append( rev_SM_sig , SM_sig)
    wavelet = numpy.append(wavelet, wavelet)
    wavelet = numpy.append(wavelet, numpy.array([0]))

    return wavelet



def triangle_pattern(AO_resolution, freq):
    step = 360.0/5000      #...step(/microstep) angle (degree)
    amp = 90        *2 #...sine wave amplitude (peak to peak degree)
    
#    Y = numpy.arange(0,amp,step)   
#    X = Y/freq/amp
    
    Y = numpy.arange(0,amp,step)   
    X = Y/freq/amp
    
    Xs = numpy.fix( X / AO_resolution )

    SM_sig = numpy.zeros(numpy.fix(Xs[numpy.size(Xs)-1])+1)
    for i in range(numpy.size(Xs)): SM_sig[Xs[i]]=1

    rev_SM_sig = numpy.zeros(numpy.fix(Xs[numpy.size(Xs)-1])+1)
    for i in range(numpy.size(SM_sig)): rev_SM_sig[i]=SM_sig[numpy.size(SM_sig)-1-i]

    wavelet = 5 * numpy.append( rev_SM_sig , SM_sig)
    wavelet = numpy.append(wavelet, wavelet)
    wavelet = numpy.append(wavelet, numpy.array([0]))
    
    return wavelet

# ######################################################################

if __name__ == '__main__':
    import time
    import numpy
    # Constant
    Rec_Period = 7     #... second
    AO_resolution = 5e-6          # (us) resolution: 200k Hz maximum, the period of which is 5 us

    # Variable
    freq = 1     #...sine wave frequency (Hz)
    
#    stim = cos_pattern(AO_resolution, freq)
    stim = cos_pattern(AO_resolution, freq)


# ###########################
    cycle= int(Rec_Period * freq )

    
    for i in range(cycle):
    
        A_out = WaveformThread( stim, stim, 1/AO_resolution)
#        A1_out = WaveformThread( 1, wavelet, 1/AO_resolution)
        D_out = DigitalOutThread(freq)
        
        D_out.start()
        A_out.start()
#        A1_out.start()

        time.sleep( (1.0/freq) + 0.001 )    # <<<====================stimuli interval
        
        A_out.stop()
#        A1_out.stop()
        D_out.stop()
