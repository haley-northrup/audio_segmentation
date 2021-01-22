import os 
import pandas as pd 
import numpy as np 
import pickle 
from IPython import embed

''' Spot Check Segmentation Outputs 
''' 

def _read_file_by_lines(filename):
    """
    Read a file into a list of lines
    """
    with open(filename, "r") as f:
        return f.read().splitlines()


#PATHS TO SEGMENT OUTPUTS 
num_jobs = 10
transcript_paths = '/nfs/turbo/chai-health/hnorthru/code/audio_segmentation/Microsoft_Azure/trans_paths/pv3/'
seg_set_paths = [os.path.join(transcript_paths, 'ma_pv3_dec2020_not_usa_r21_set_paths_' + str(i) + '.txt') for i in range(0, num_jobs)]
output_dir='/scratch/emilykmp_root/emilykmp/hnorthru/priori_v3_data_Dec_2020/segments/'
seg_folders = [os.path.join(output_dir, 'seg_' + str(i))  for i in range(0, num_jobs)]

#CHECK COUNTS 
for n in range(0, num_jobs):
    sf = seg_folders[n]
    print('Folder: ' + sf)
    tp = seg_set_paths[n]
    
    # Number of Files 
    wavs = os.path.join(sf, 'wav')
    word_time = os.path.join(sf, 'word_timing')
    meta_df = pd.read_csv(os.path.join(sf, 'ma_segments.csv'))
    if len(os.listdir(wavs)) != meta_df.shape[0]:
        print('*****Inconsistent # segment wav files as metadata rows')
    elif len(os.listdir(word_time)) != meta_df.shape[0]:
        print('*****Inconsistent # word timing files as metadata rows')
    else:
        print('File counts match!')


    #File Names 
    wav_files = os.listdir(wavs)
    wav_file_names = [os.path.splitext(w)[0] for w in wav_files]
    wt_files = os.listdir(word_time) 
    wt_file_names = [os.path.splitext(w)[0] for w in wt_files]

    if len(set(wav_file_names).difference(set(wt_file_names))) > 0:
        print('******* Inconsistent file names between wavs and word timing')
    elif len(set(meta_df['segment_id'].values).difference(set(wav_file_names))) > 0:
        print('******* Inconsistent file names between wavs and metadata')
    else:
        print('File names match!') 

    #Check correct subjects in set
    seg_output_paths = _read_file_by_lines(tp) 
    sub_ids = [s.split('/')[6] for s in seg_output_paths]
    sub_ids = np.array(sub_ids) 
    meta_df['subject_id'] = meta_df['subject_id'].astype(int).astype(str) 
    for sid in np.unique(sub_ids):
        num_sets = np.sum(sub_ids == sid) 
        meta_sub = meta_df.loc[meta_df['subject_id'] == sid]
        
        if num_sets*100 < len(meta_sub['call_id'].unique()):
            print(sid)
            print('MORE CALLS THAN EXPECTED!!')

        
    #Quick word timing file check 
    with open(os.path.join(word_time, wt_files[0]), 'rb') as f:
        word_timing_example = pickle.load(f)
        print(word_timing_example) 


# Total Number of Files Matches sum of individual jobs 
all_seg_meta_df = pd.read_csv(os.path.join(output_dir, 'ma_segments.csv'))
file_counts = []
for n in range(0, num_jobs):
    sf = seg_folders[n]
    #print('Folder: ' + sf)
    meta_df = pd.read_csv(os.path.join(sf, 'ma_segments.csv'))
    #print(meta_df.shape[0])
    file_counts.append(meta_df.shape[0]) 

if all_seg_meta_df.shape[0] != np.sum(file_counts):
    print('TOTAL FILE COUNTS DO NOT MATCH!!!!')
else: 
    print('Total File Counts Match!')
    print(all_seg_meta_df.shape)

#CHECK START AND END FILES 
#cols = ['call_id', 'segment_num', 'subject_id', 'call_datetime', 'is_assessment', 'device', 'duration_ms']
cols = ['call_id', 'segment_number', 'subject_id', 'is_assessment', 'duration_ms']

start_idx = 0 
for n in range(0, num_jobs):
    sf = seg_folders[n]
    print('Folder: ' + sf)
    meta_df = pd.read_csv(os.path.join(sf, 'ma_segments.csv'))
    end_idx = start_idx + meta_df.shape[0] - 1

    #Check start file 
    print(start_idx)
    if meta_df.iloc[0][cols].values.any() != all_seg_meta_df.iloc[start_idx][cols].values.any():
        print('Start files not aligned') 

    #Check end file  
    print(end_idx) 
    if meta_df.iloc[meta_df.shape[0]-1][cols].values.any() != all_seg_meta_df.iloc[end_idx][cols].values.any():
        print('End files not aligned') 
        
    start_idx = end_idx + 1