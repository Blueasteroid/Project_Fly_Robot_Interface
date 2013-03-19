function result = FR2W_collection(file, sum_period)

% file='H:\[DAQ_DATA]\Data_3Ch_[2013-03-16_22-40-06]_TOP9_180degHz.mat'

disp(file)

raw_data = load(file, 'vect'); 
data = raw_data.vect;

%% Parameter loading

SamplingRate = 20000;
Fs=SamplingRate;
TotalPeriod = 10;
t=[0:1/SamplingRate:TotalPeriod-1/SamplingRate];


%% Data analysis (spike train detection)


threshold = 2.5-0.20;


spike_train(1:2,1:SamplingRate*TotalPeriod) = 0;
i=2;
while(SamplingRate*TotalPeriod +1 - i )
    %...spike_train 1
    if ((data(1,i)>=threshold) && (data(1,i-1)<=threshold)) %... rising edge
         spike_train(1,i)=1;
    end
    
    i=i+1;
end



%% Data process (1st 100ms firing rate)
avrage_spike_rate(1,1:SamplingRate*TotalPeriod) = 0;
tag = 1;
SM_dir_threshold = 1;


% sum_period = 0.200; %...ms
sum_samples = sum_period * Fs ;


j=1;
i=2;
while(SamplingRate*TotalPeriod +1 - i )
    if (xor((data(3,i)>=SM_dir_threshold) , (data(3,i-1)>=SM_dir_threshold))) %... edge

%         avrage_spike_rate(1,tag:i) = sum(spike_train(1,tag:i))/((i-tag)/SamplingRate);
%         Measured_Period = (i - tag) / SamplingRate;
        
        des = min((tag+sum_samples),i);
        Measured_Period = (des-tag)/Fs;        
        avrage_spike_rate(1,tag:i) = sum(spike_train(1,tag:des))/Measured_Period;


        pre_result(1,j) = avrage_spike_rate(1,tag); %sum(spike_train(1,tag:i))/((i-tag)/SamplingRate);
        pre_result(2,j) = Measured_Period;
        j=j+1;
        
        tag = i;
    end
    i=i+1;
end

[foldername, filename, extname] = fileparts(file);

if (strcmp ('BOT' , filename(32:34)) )
    result(1,1) = pre_result(1,3);
    result(3,1) = 1 ;
else
    result(1,1) = pre_result(1,4);
    result(3,1) = 0 ; 
end
result(2,1) = str2num(filename(37:length(filename)-5));


% k=1;
% for i=1:length(pre_result(1,:))
%     if pre_result(2,i)<=0.0002
%         result(2,k)=abs(pre_result(1,i-1)-pre_result(1,i-2));
%         result(1,k)=((pre_result(2,i-1)+pre_result(2,i-2)))/2;
%         result(1,k)=360/30/result(1,k);
%         k=k+1;
%     end
% end

% return result
end
