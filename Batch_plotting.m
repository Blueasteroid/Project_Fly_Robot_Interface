%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Jiaqi (Joseph) Huang
% Imperial College London
% Batch plotting
% 2013-01-16
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear
folder = 'G:\[JH4209]\[JH][Recording]\REC_2013-03-16_FLY12\'; 
% folder = 'H:\[DAQ_DATA]\';
dirListing = dir(folder);

for i = 1:length(dirListing)
    if ~dirListing(i).isdir 
        fileName = fullfile(folder,dirListing(i).name); % use full path because the folder may not be the active path

        hFig = figure (1);
        set(hFig,'Visible','off');
        Data_processing_ISI_plotting(fileName, hFig);

        [foldername, filename, extname] = fileparts(fileName);

        print(hFig, '-dmeta', fullfile(strcat(foldername,'\fig'),strcat(filename,'.emf')))  
%         saveas(hFig, fullfile(foldername, strcat(filename,'.emf')))
        
    end % if-clause
end % for-loop
