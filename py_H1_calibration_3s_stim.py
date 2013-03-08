from nidaqmx import *
import time
import numpy
import scipy.io as sio
import threading
import sys
#import matplotlib.pyplot as pylab

#=======================================================
'''
def stim(w=360):
    global SM_step
    SM_step = 360.0/5000.0      #...step(/microstep) angle (degree)
    amp = 360.0 /2              #...sine wave amplitude (peak to peak degree)
    freq = 1.0/3                  #...sine wave frequency (Hz)

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
'''

def stim_gen(w=30, t=3, dir_seq = 0):
    SM_step = 360.0/5000.0      #...step(/microstep) angle (degree)
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
    freq = 5
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
#        return data
    
# time=numpy.arange(start=0,stop=t,step=1/200000)
# plot(time,data)

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
    def __init__(self, name, w):#,t):
        threading.Thread.__init__( self )
        
        self.name = name        
        
        self.w = w
#        self.t = t
        self.AI_rate = 20000
        self.sampling_time = 20     #... second
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
#        print "Stimulation Fs: %d" %(self.AO_rate)
#        print "Stimulation Fs: %s" %(self.AO_data)
#        print "Stimulation Fs: %d" %(numpy.size(self.AO_data))

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
#    w = 360    # for easier data processingmax_w
#    tLmt = SM_step / w

#    max_w = 300
#    div = 10
#    t = 3   
#    name = 'NAT5'
    
#------------------------- 
    '''
    w=30
    AO = AO_threading(w,t)    
    AI = AI_threading(w)

    AI.start()
    time.sleep(0.5)        
    AO.start()

    while AO.is_alive():
        pass
    while AI.is_alive():
       pass
         
            
#-------------------------



    if len(sys.argv)==2:
        if str(sys.argv[1])=='test':
            
            for i in range(1,div):
                w = w_max*(i+1)/div
                
                print "Testing angular velocity: %d" %(w)
                
                AO = AO_threading(w)
                AO.start()

                while AO.is_alive():
                    pass
    elif len(sys.argv)==3:
        if str(sys.argv[1])=='test':
            w = int(sys.argv[2])
            
            if w>720:
                w=720
            elif w<54:
                w=54
            else:
                pass
            
            print "Testing angular velocity: %d" %(w)
            AO = AO_threading(w)
            AO.start()
            while AO.is_alive():
                pass
    else:
    '''        
    
    max_w = 300
#    div = 10
    t = 3
    div = 10  
    
#========= parameter setting ==================== 
    num = 1 
    name = 'BOT' + str(num)
    dir_seq = 0
    
#========= test run ==================== 
    w = 60
    stim=stim_gen(w, t, dir_seq )   
    AO = AO_threading(w,stim)
    AO.start()
    while AO.is_alive():
        pass
    
    
#========= seq shuffle ====================   
#    seq = numpy.arange(div)
#    numpy.random.shuffle(seq)
#==========================================   

    seq = numpy.array([5,0,1,6,9,8,3,7,2,4])
    div = numpy.size (seq)
    if ((num % 2) is 1):
        seq = seq[::-1]


    for i in seq:
        w = max_w*(i+1)/div
        
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

      
  
