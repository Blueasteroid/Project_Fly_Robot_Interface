function figH = Data_processing_ISI_plotting(file_location, figH)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Jiaqi (Joseph) Huang
% Imperial College London
% Spike train and ISI rate plot
% 2012-10-01
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Initialization
% close all;

%% Data loading
% dir = 'G:\[JH4209]\[JH][Rec]\';
% filename = 'Data_3Ch_2012-10-04_20-08-47_[]'

% dir = 'H:\[DAQ_DATA]\';
% filename = 'Data_3Ch_SB_2013-01-15_17-33-08_[0.3check].mat'



raw_data = load(file_location, 'vect'); 
% raw_data = load(strcat(dir,filename,'.mat'), 'vect'); 

data(1,:) = raw_data.vect{1};
data(2,:) = raw_data.vect{2};
data(3,:) = raw_data.vect{3};

%% Parameter loading

SamplingRate = 20000;
Fs=SamplingRate;
TotalPeriod = 10;
t=[0:1/SamplingRate:TotalPeriod-1/SamplingRate];

% threshold = 2.55;

%% Data analysis (spike train detection)


threshold = 2.5-0.25;


spike_train(1:2,1:SamplingRate*TotalPeriod) = 0;
i=2;
while(SamplingRate*TotalPeriod +1 - i )
    %...spike_train 1
    if ((data(1,i)>=threshold) && (data(1,i-1)<=threshold)) %... rising edge
         spike_train(1,i)=1;
    end
    
    i=i+1;
end

%% Data analysis (oscillation frequency measurement)
prev_trig=0;
curr_trig=0;
i=2;
while(SamplingRate*TotalPeriod +1 - i )
    
    if ((data(3,i)>=2.5) && (data(3,i-1)<=2.5)) %... rising edge
     prev_trig = curr_trig;
     curr_trig = i;
    end
    
    i=i+1;
end
Measured_Period = (curr_trig - prev_trig) / SamplingRate;
Measured_frequency = 1 / Measured_Period;
disp(strcat('The oscillation frequency is: ' , num2str(Measured_frequency)))

%% Data process (firing rate)

window = 1000;
spike_rate(1)= 0; 

for i=1:length(spike_train(1,:))
    if (i<=window)
        spike_rate(i) = abs(sum(spike_train(1,1:i))) ;
    else
        spike_rate(i) = abs(sum(spike_train(1,i-window:i))) ;
    end
end
spike_rate = spike_rate .* (SamplingRate/window);

%% Data process (ISI rate calculation)

ISI_rate(1,1:SamplingRate*TotalPeriod) = 0;
prev_spk_idx = 1;
curr_spk_idx = 1;
for i=1:length(spike_train)
    curr_spk_idx = i;
    if (spike_train(1,i)==1)
        ISI_rate(1,prev_spk_idx:curr_spk_idx) = SamplingRate/(curr_spk_idx-prev_spk_idx);
        prev_spk_idx = curr_spk_idx;
    end
end


%% Data Drawing
subplot_row = 2;
subplot_col = 1;

% figH = figure(figno);
set(figH,'Name',file_location,'NumberTitle','off')


h(1) = subplot(subplot_row, subplot_col,1);
plot(t,data(1,:),'b',t,data(2,:),'r');
hold on
plot(t,data(3,:),'black') %,'b',t,spike_train(2,:)./5+2
hold off
line([0 TotalPeriod], [threshold threshold],'Color','green'); %...threshold line
xlabel('Time(sec)')
ylabel('Potential(V)')
title(strcat('Blowfly stimulated at:',32,num2str(Measured_frequency),' osc/sec yaw rotation'))


h(2) = subplot(subplot_row, subplot_col,2);
stem(t,400*spike_train(1,:),'k','Marker','none')%max(ISI_rate(1,:))
hold on
plot(t,ISI_rate(1,:),'r') %,'b',t,spike_train(2,:)
plot(t,spike_rate(1,:),'g')
hold off
axis([0 10 0 400]);
xlabel('Time(sec)')
ylabel('Spike train & ISI rate')
title(strcat('Spike train and ISI rate plot'))

linkaxes(h,'x');
