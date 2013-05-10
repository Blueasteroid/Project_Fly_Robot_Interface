from nidaqmx import *
import time
import numpy
import scipy.io as sio
import threading
import sys
#import matplotlib.pyplot as pylab

#=======================================================
#=======================================================
def stim_gen(w=30, t=3, dir_seq = 0):
    SM_step = 360.0/50000.0      #...step(/microstep) angle (degree)
#    Fs = w/SM_step    
    Fs=200000
    pulse_rate = w/SM_step    
# -------------------------------------------------------    
    
    pwm=[5]
    for i in range( int(Fs/pulse_rate)-1 ):
        pwm = numpy.append(pwm,[0])
        
    sec=pwm   
    for i in range( int(pulse_rate) ):
        sec = numpy.append(sec,pwm)    
        
    sec=sec[0:200000]    
    
    pulse_train=sec
    for i in range( t-1 ):
        pulse_train = numpy.append(pulse_train,sec)  
        
    pulse_train = numpy.float64(pulse_train) 
    
# -------------------------------------------------------
#    amp=360.0
    freq = 1
    amp = w/(2*numpy.pi*freq)
    Y = numpy.arange(0,amp,SM_step)   
    X = (1/(2*numpy.pi*freq))*numpy.arcsin(Y/amp)
    
#    Xs = numpy.fix(X * (200000.0/20) )
#    X = numpy.arange(0,1/freq/4,1/20000)  
#    Y = amp * numpy.cos(2 * numpy.pi * freq * X)

    Xs=numpy.fix(X*Fs)
    
    SM_dec = numpy.zeros(numpy.fix(Xs[numpy.size(Xs)-1])+1)    #... numpy.size(Xs)-1
    for i in range(numpy.size(Xs)): SM_dec[Xs[i]]=5
    
    SM_acc=SM_dec[::-1]
        
#    figure();  plot(X,Y);  stem(X,Y)   #...debug
    
    pulse_train = numpy.append(SM_acc, pulse_train)    
    pulse_train = numpy.append(pulse_train,SM_dec)
    
# -------------------------------------------------------    
    SM_pulse_CW = pulse_train
    SM_pulse_CCW = pulse_train
    SM_pulse = numpy.append(SM_pulse_CW,SM_pulse_CCW)
    
    L = numpy.size(SM_pulse)/2
    
    SM_dir_CW = 5*numpy.ones(L,dtype=numpy.float64)
    SM_dir_CCW = numpy.zeros(L,dtype=numpy.float64)
    if (dir_seq is 0):
        SM_dir = numpy.append(SM_dir_CW,SM_dir_CCW)
    else:
        SM_dir = numpy.append(SM_dir_CCW,SM_dir_CW)
    

    # for easier data processing
    sig_head = 5*numpy.ones(20)
    sig_tail = numpy.append(numpy.zeros(20),5*numpy.ones(20))
    sig_tail = numpy.append(sig_tail,numpy.zeros(1))
    SM_pulse = numpy.append(sig_head,SM_pulse)
    SM_pulse = numpy.append(SM_pulse,sig_tail)
    SM_dir = numpy.append(sig_head,SM_dir)
    SM_dir = numpy.append(SM_dir,sig_tail)
    # ==========================
    
    data = numpy.append(SM_pulse,SM_dir)  
    return {'data' : data, 'Fs' : Fs}
    
#=======================================================
#=======================================================
class AI_threading(threading.Thread):
    def __init__(self, name, w):#,t):
        threading.Thread.__init__( self )
        
        self.name = name        
        
        self.w = w
#        self.t = t
        self.AI_rate = 20000
        self.sampling_time = 10     #... second
        self.channel = 3
        self.max_num_samples = self.AI_rate * self.sampling_time * self.channel
        self.data = numpy.zeros(self.max_num_samples)  #numpy.zeros((max_num_samples,),dtype=numpy.float64)
        
    def run(self):
        AI_task = AnalogInputTask()
        AI_task.create_voltage_channel('Dev6/ai1:3', terminal = 'diff', min_val=-10.0, max_val=10.0)
        AI_task.configure_timing_sample_clock(rate = self.AI_rate)

        #del task
        #from pylab import plot, show
        #plot (data)
        #show ()
        
        print "Recording... "     #... debug
        AI_task.start()
        self.data = AI_task.read(samples_per_channel= self.AI_rate * self.sampling_time, fill_mode='group_by_channel',timeout = self.sampling_time )

        print "Recording complete! "
        vect = self.data
        matfilename = 'Data_3Ch_[' + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + ']_' + self.name + '_' + str(self.w) + 'degHz.mat'
        sio.savemat (matfilename,{'vect':vect})
        print "Data saved! in file: %s" % (matfilename)   #... debug
        
#=======================================================        

class AO_threading(threading.Thread):
    def __init__(self,w,stim):
        threading.Thread.__init__( self )

#        self.sampling_time = 10      #... second
        self.w = w
        self.t = 3
#        stim=stim_gen(w=self.w, t=self.t, seq=1)
        self.stim=stim
        self.AO_data = self.stim['data']     # <<=== stimulus loading ===
        self.AO_rate = 200000        
    
    def run(self):
        print "Stimulation running... at %d deg/sec " % (self.w)
#        rep = int(self.sampling_time / (tLmt*2*5000+1))
#        for i in range(rep):
        AO_task = AnalogOutputTask()
        AO_task.create_voltage_channel('Dev5/ao0:1', min_val=-10.0, max_val=10.0)
        AO_task.configure_timing_sample_clock(rate = self.AO_rate) 
        AO_task.set_regeneration(0)
        AO_task.write(self.AO_data, auto_start=False, layout = 'group_by_channel')
        AO_task.start()
#            print "Stimulation repetition: %d / %d" %((i+1),rep)
        time.sleep(2*self.t+1)   #tLmt*2*5000+1)


#=======================================================
#=======================================================
if __name__ == '__main__':
    
    
    max_w = 300
#    div = 10
    t = 3
    div = 10  
    
    
    SM = 'BOT'   
    # dir_seq = 0
    # NAT,BOT = 0, TOP = 1
    if (SM=='BOT'): dir_seq = 0
    if (SM=='TOP'): dir_seq = 1
    
    for k in range(div): 
    
#========= parameter setting ==================== 

        num = k
        
        name = SM + str(num)

    #========= test run ==================== 
        print "Test run... "
        w = 60
        stim=stim_gen(w, t, dir_seq )   
        AO = AO_threading(w,stim)
        AO.start()
        while AO.is_alive():
            pass
        print "Test run over. "
        
    #========= seq shuffle ====================   
    #    seq = numpy.arange(div)
    #    numpy.random.shuffle(seq)
    #==========================================   
    
        # angv = numpy.array([5, 10, 15, 30, 45, 60, 75, 120, 195, 300])
        angv = numpy.array([3, 15, 45, 60, 75, 120, 165, 210, 255, 300]) 
        seq = numpy.array([5,0,1,6,9,8,3,7,2,4])
        div = numpy.size (seq)
        if ((num % 2) is 1):
            seq = seq[::-1]
    
    
        for i in seq:
            #w = max_w*(i+1)/div
            w = angv[i]            
            
            stim=stim_gen(w, t, dir_seq )    
            
            AI = AI_threading(name, w)
            AO = AO_threading(w,stim)
    
            AI.start()
            time.sleep(0.5)
            AO.start()
    
            while AO.is_alive():
                pass
            while AI.is_alive():
                pass
