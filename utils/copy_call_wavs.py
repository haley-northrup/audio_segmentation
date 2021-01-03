''' Copy select segments and call audio into folder 


'''

import os 
import pandas as pd 
import numpy as np 
from IPython import embed 
from shutil import copyfile 


# SET UP 
#********************

#call_ids = [37699, 40763, 42237, 33147] #set1
#call_ids = [34665, 48381, 1875, 20679] #set2 
#call_ids = [17920, 36505, 11795, 50234, 31301, 25502] #set3
#call_ids = [44692, 45651, 50322, 28516, 28681, 25422] #set4 
#call_ids = [38136, 42191, 34758, 13441] #set5 
call_ids = [8023, 9642, 21202] #set6 
n = 4

#PATHS 
outdir = './analysis_audio/set6'

call_wav_path = '/nfs/turbo/McInnisLab/priori_v1_data/call_audio/speech/' 

seg_meta_path1 = '/nfs/turbo/McInnisLab/priori_v1_data/collections/emotion_preds.csv'
call_data_path1 = './soheil_VAD/call_seg_metadata.csv'
seg_wav_path1 = '/nfs/turbo/McInnisLab/priori_v1_data/segments_all/wav/' 

seg_meta_path2 = '/nfs/turbo/McInnisLab/PRIORI_v1_Microsoft_Azure/PRIORI-v1-Microsoft-segments/priori_v1_ma_segments.csv'
call_data_path2 = './microsoft_azure/call_seg_metadata.csv'
seg_wav_path2 = '/nfs/turbo/McInnisLab/PRIORI_v1_Microsoft_Azure/PRIORI-v1-Microsoft-segments/wav' 

#Load Metadata 
seg_meta_soh = pd.read_csv(seg_meta_path1)
call_meta_soh = pd.read_csv(call_data_path1)
seg_meta_ma =  pd.read_csv(seg_meta_path2)
call_meta_ma =  pd.read_csv(call_data_path2)


#Copy files for analysis 
#*****************************
for c in call_ids:
    #Make folders 
    call_dir = os.path.join(outdir, str(c))
    if not os.path.exists(call_dir): 
        os.makedirs(call_dir) 
    if not os.path.exists(os.path.join(call_dir, 'microsoft_azure')): 
        os.makedirs(os.path.join(call_dir, 'microsoft_azure')) 
    if not os.path.exists(os.path.join(call_dir, 'soheil_VAD')): 
        os.makedirs(os.path.join(call_dir, 'soheil_VAD')) 
        
    #Copy call .wav file 
    call_wav = os.path.join(call_wav_path, str(c) + '.wav')
    dest_wav = os.path.join(call_dir, str(c) + '.wav')
    copyfile(call_wav, dest_wav)

    #Get first n segments from call 
    #soheil_VAD 
    soh_segs = seg_meta_soh.loc[seg_meta_soh['call_id'] == c, :].sort_values('segment_order') 
    seg_ids = soh_segs['segment_id'].values 
    soh_df = call_meta_soh.loc[call_meta_soh['call_id'] == c, :] 
    if len(seg_ids) > 0:
        for s in range(0, min(n, len(seg_ids))):
            seg_wav = os.path.join(seg_wav_path1, str(seg_ids[s]) + '.wav')
            dest_wav = os.path.join(call_dir, 'soheil_VAD', str(seg_ids[s]) + '.wav')       
            copyfile(seg_wav, dest_wav)
    soh_df.to_csv(os.path.join(call_dir, 'soheil_VAD','meta.csv'), index=False) 

    #microsoft_azure  
    ma_segs = seg_meta_ma.loc[seg_meta_ma['call_id'] == c, :].sort_values('segment_number') 
    seg_ids = ma_segs['segment_id'].values 
    ma_df = call_meta_ma.loc[call_meta_ma['call_id'] == c, :] 
    if len(seg_ids) > 0:
        for s in range(0, min(n, len(seg_ids))):
            seg_wav = os.path.join(seg_wav_path2, str(seg_ids[s]) + '.wav')
            dest_wav = os.path.join(call_dir, 'microsoft_azure', str(seg_ids[s]) + '.wav')       
            copyfile(seg_wav, dest_wav)
    ma_df.to_csv(os.path.join(call_dir, 'microsoft_azure', 'meta.csv'), index=False) 











