%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Jiaqi (Joseph) Huang
% Imperial College London
% Batch info collection
% 2013-01-29
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear;close all;
% folder = 'G:\[JH4209]\[JH][Working]\JH_Matlab_batch_plotting_folder\data_29-01-2013_trial1\data_NAT\'; 
folder = 'G:\[JH4209]\[JH][Recording]\REC_FLY12'; 
% folder = 'H:\[DAQ_DATA]\';
dirListing = dir(folder);

T_samp = 100; %...ms

info = [0.0;0.0;0.0;0.0];
for i = 1:length(dirListing)
%     clear

    if ~dirListing(i).isdir 
        fileName = fullfile(folder,dirListing(i).name); % use full path because the folder may not be the active path


%         hFig = figure (1);
%         set(hFig,'Visible','off');=87 
%         Data_processing_ISI_plotting(fileName, hFig);

        data = Func_FR_collection(fileName, T_samp/1000);
        data = [data;i];
        info = [info data];
        
%         [foldername, filename, extname] = fileparts(fileName);

%         print(hFig, '-dmeta', fullfile(strcat(foldername,'\fig'),strcat(filename,'.emf')))  
%         saveas(hFig, fullfile(foldername, strcat(filename,'.emf')))
        
    end % if-clause
end % for-loop
info = info(:,2:length(info));


% figure(1)
% % plot(info(1,:),info(2,:),'*')
% xlabel('Contrast frequency (cycle/s)')
% ylabel('Spike rate (spike/s)')
% title('Turning Curve')

% print(gcf, '-dmeta', fullfile(strcat(folder),strcat('turning_curve','.emf')))

%% average plot
% 
% s = sort (info,2);
% 
% j=1;
% k=1;
% temp1=0;temp2=0;
% for i=2:length(s(1,:))
%     if (fix(s(1,i))==fix(s(1,i-1)))
%         temp1 = temp1 + s(1,i);
%         temp2 = temp2 + s(2,i);
%         k=k+1;
%     else
%         res(1,j)=temp1/k;
%         res(2,j)=temp2/k;
%         temp1=0;temp2=0;
%         k=1;
%         j=j+1;
%     end
% end
% 
% figure(2)
% plot(res(1,:),res(2,:))
% xlabel('Angular velocity (deg/s)')
% ylabel('Spike rate (spike/s)')
% title('Turning Curve')

%% save data info

save(fullfile(strcat(folder,'\info'),strcat(folder(33:length(folder)),'_info_',num2str(T_samp),'ms.mat')), 'info');

%% plotting dots

figure(1)

% subplot(211)
% plot(info(2,1:61),info(1,1:61),'.')
% subplot(212)
% plot(info(2,62:161),info(1,62:161),'.')

plot(info(2,1),info(1,1),'.r')
hold on
for i=2:length(info)
    if (info(3,i)==1)
        plot(info(2,i),info(1,i),'.r')
    else
        plot(info(2,i),info(1,i),'ob')
    end
end
hold off

xlabel('Angular velocity (deg/s) @ (spatial wavelength = 30 deg)')
ylabel('Spike rate (spike/s)')
title('Tuning Curve: red(self motion), blue(background motion)')
axis([0 330 0 400])
grid on

print(gcf, '-dmeta', fullfile(strcat(folder,'\info'),strcat(folder(33:length(folder)),'_trial_',num2str(T_samp),'ms.emf')))  

%% ploting mean std

infoT=info';
infoS=sortrows(infoT,2);
infoR=infoS';

trial = 10;
for i=1:10
   X(i)=i*30;
   Ys(i)= mean(infoR(1,(2*i-2)*10+1:(2*i-2)*10 + trial ));
   Yb(i)= mean(infoR(1,(2*i-1)*10+1:(2*i-1)*10 + trial ));
   Es(i)= std (infoR(1,(2*i-2)*10+1:(2*i-2)*10 + trial ));
   Eb(i)= std (infoR(1,(2*i-1)*10+1:(2*i-1)*10 + trial ));
end

figure
errorbar(X,Ys,Es,'r')
hold on
errorbar(X,Yb,Eb)
hold off

xlabel('Angular velocity (deg/s) @ (spatial wavelength = 30 deg)')
ylabel('Spike rate (spike/s)')
title('Tuning Curve with errorbar: red(self motion), blue(background motion)')
axis([0 330 0 400])

print(gcf, '-dmeta', fullfile(strcat(folder,'\info'),strcat(folder(33:length(folder)),'_errorbar_',num2str(T_samp),'ms.emf')))

