from nidaqmx import *
import time
import numpy
import scipy.io as sio
import threading
import sys
#import matplotlib.pyplot as pylab

#=======================================================
def stim(w=360):
    global SM_step
    SM_step = 360.0/5000.0      #...step(/microstep) angle (degree)
    amp = 360.0 /2              #...sine wave amplitude (peak to peak degree)
    freq = 1                  #...sine wave frequency (Hz)

    Y = numpy.arange(0,amp,SM_step)   
    X = (1/(2*numpy.pi*freq))*numpy.arcsin(Y/amp)

    #w = 180.0                   #... deg/sec
    #tLmt = (360.0/w)/4/(SM_step)
    #tLmt = 1.0/5000
    global tLmt
    tLmt = SM_step / w          #... sec/step

    dX = numpy.zeros(numpy.size(X))
    dX[0] = X[0]
    for i in range(1, numpy.size(X)-1): dX[i] = X[i] - X[i-1]

    for i in range(1,numpy.size(X)):
        if dX[i] < tLmt: dX[i] = tLmt

    XX = numpy.zeros(numpy.size(X))
    for i in range(1,numpy.size(XX)): XX[i] = XX[i-1] + dX[i]

    #    pylab.plot(X,Y);pylab.show();

    AO_resolution = 5e-6          # (us) resolution: 200k Hz maximum, the period of which is 5 us    

    Xs = numpy.fix(XX / AO_resolution )

    SM_sig = numpy.zeros(numpy.fix(Xs[numpy.size(Xs)-1])+1)    #... numpy.size(Xs)-1
    for i in range(numpy.size(Xs)): SM_sig[Xs[i]]=1

    rev_SM_sig = numpy.zeros(numpy.fix(Xs[numpy.size(Xs)-1])+1)
    for i in range(numpy.size(SM_sig)): rev_SM_sig[i]=SM_sig[numpy.size(SM_sig)-1-i]

    #    duration = 2 * X[numpy.size(X)-1]    # (second) duration of the signal train

    wavelet = 5 * numpy.append( rev_SM_sig,SM_sig )
    wavelet = numpy.append(wavelet, wavelet)
    wavelet = numpy.append(wavelet, numpy.array([0]))

    SM_dir = numpy.append(5*numpy.ones(numpy.size(rev_SM_sig)+numpy.size(SM_sig)),numpy.zeros(numpy.size(rev_SM_sig)+numpy.size(SM_sig)))
    SM_dir = numpy.append(SM_dir, numpy.array([0]))

    # for easier data processing
    sig_head = 5*numpy.ones(20)
    sig_tail = numpy.append(numpy.zeros(20),5*numpy.ones(20))
    sig_tail = numpy.append(sig_tail,numpy.zeros(1))
    SM_pulse = numpy.append(sig_head,wavelet)
    SM_pulse = numpy.append(SM_pulse,sig_tail)
    SM_dir = numpy.append(sig_head,SM_dir)
    SM_dir = numpy.append(SM_dir,sig_tail)

    stim = numpy.append(SM_pulse, SM_dir)
                                                                    
    #wavelet = 5 * numpy.ones(40000)
    return stim

#=======================================================
# data = 9.95*np.sin(np.arange(1000, dtype=np.float64)*2*np.pi/1000)

#DO = DigitalOutputTask()
#DO.create_channel('Dev5/port1/line0', grouping='for_all_lines')
#DO.configure_timing_sample_clock()

#DO.write(numpy.zeros((4,), numpy.uint8 ), auto_start=False)
#DO.start()

#AO.wait_until_done(timeout = 10)

#while ~AO.is_done():
#    time.sleep(1)

#time.sleep(1.0/freq)
#    AO.stop()

#raw_input('Generating voltage continuously. Press Enter to interrupt...')
#AO.stop()
#DO.stop()
#del DO
#=======================================================
class AI_threading(threading.Thread):
    def __init__(self,w):
        threading.Thread.__init__( self )

        self.sampling_rate = 20000
        self.sampling_time = 10      #... second
        self.channel = 3
        self.max_num_samples = self.sampling_rate * self.sampling_time * self.channel
        self.data = numpy.zeros(self.max_num_samples)  #numpy.zeros((max_num_samples,),dtype=numpy.float64)
        self.w = w
        
    def run(self):
        AI_task = AnalogInputTask()
        AI_task.create_voltage_channel('Dev6/ai1:3', terminal = 'diff',min_val=-10.0, max_val=10.0)
        AI_task.configure_timing_sample_clock(rate = self.sampling_rate)

        #del task
        #from pylab import plot, show
        #plot (data)
        #show ()
        
        print "Recording... "     #... debug
        AI_task.start()
        self.data = AI_task.read(samples_per_channel= self.sampling_rate * self.sampling_time, fill_mode='group_by_channel')

        print "Recording complete! "
        vect = self.data
        filename = 'Data_3Ch_CALI_' + str(self.w) + 'degHz_[' + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '].mat'
        sio.savemat (filename,{'vect':vect})
        print "Data saved! in file: %s" % (filename)   #... debug
        
#=======================================================        

class AO_threading(threading.Thread):
    def __init__(self, w):
        threading.Thread.__init__( self )

        self.sampling_time = 10      #... second
        self.AO_resolution = 5e-6 
        self.AO_data = stim(w)
    
    def run(self):
        rep = int(self.sampling_time / (tLmt*2*5000+1))
        for i in range(rep):
            AO_task = AnalogOutputTask()
            AO_task.create_voltage_channel('Dev5/ao0:1', min_val=-10.0, max_val=10.0)
            AO_task.configure_timing_sample_clock(rate = 1/self.AO_resolution) 
            AO_task.set_regeneration(0)
            AO_task.write(self.AO_data, auto_start=False, layout = 'group_by_channel')
            AO_task.start()
            print "Stimulation repetition: %d / %d" %((i+1),rep)
            time.sleep(tLmt*2*5000+1)

#=======================================================
#del AO_task
#del AI_task
#=======================================================

#vect = numpy.zeros((3,), dtype=numpy.object)
#vect[0]=data[0 : sampling_rate*sampling_time]
#vect[1]=data[sampling_rate*sampling_time : sampling_rate*sampling_time*2]
#vect[2]=data[sampling_rate*sampling_time*2 : max_num_samples]
#vect = data

#sio.savemat ('Data_3Ch_' + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '_SB_[].mat',{'vect':vect})
#print "Data saved! "    #... debug

#=======================================================
if __name__ == '__main__':
#-------------------------
#    SM_step = 360.0/5000.0
#    w = 360
#    tLmt = SM_step / w


    div = 10
#-------------------------
    if len(sys.argv)==2:
        if str(sys.argv[1])=='test':
            
            for i in range(div):
                w = 180+180*(i+1)/div
                
                print "Testing angular velocity: %d" %(w)
                
                AO = AO_threading(w)
                AO.start()

                while AO.is_alive():
                    pass
    elif len(sys.argv)==3:
        if str(sys.argv[1])=='test':
            w = int(sys.argv[2])
            
            if w>360:
                w=360
            elif w<180:
                w=180
            else:
                pass
            
            print "Testing angular velocity: %d" %(w)
            AO = AO_threading(w)
            AO.start()
            while AO.is_alive():
                pass
    else:
#            div = 10
        for i in range(div):
            w = 180+180*(i+1)/div
            
            AI = AI_threading(w)
            AO = AO_threading(w)

            AI.start()
            time.sleep(0.5)
            AO.start()

            while AO.is_alive():
                pass
            while AI.is_alive():
                pass
            
        
  
