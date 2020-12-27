import os 
import pandas as pd 
import numpy as np 
import pickle 
from shutil import copyfile 
from IPython import embed

''' Combine Segmentation output sets 

If segmentation is run in separate slurm jobs, 
individual folders will be generated for each job

Each folder: 
    segments - folder of wav files 
    word_timing - folder of word_timing pickle files
    priori_v1_ma_segments.csv
    priori_v1_ma_segments_with_trans.csv 
''' 

def _read_file_by_lines(filename):
    """
    Read a file into a list of lines
    """
    with open(filename, "r") as f:
        return f.read().splitlines()

#PATHS TO SEGMENT OUTPUTS 
num_jobs = 10 
seg_path ='/nfs/turbo/McInnisLab/PRIORI_v1_Microsoft_Azure/PRIORI-v1-Microsoft-segments'
metadata_fn = 'priori_v1_ma_segments'
seg_folders = [os.path.join(seg_path, 'seg_' + str(i))  for i in range(0, num_jobs)]
comb_wav_dir = os.path.join(seg_path, 'wav')
comb_wt_dir = os.path.join(seg_path, 'word_timing')

#CHECK COUNTS 
for n in range(0, num_jobs):
    sf = seg_folders[n]
    print('Folder: ' + sf)

    #get metadata
    meta_df = pd.read_csv(os.path.join(sf, metadata_fn + '.csv'))
    meta_df = meta_df.sort_index() #order by segment_id (ma0, ma1, ma2...)
    meta_df['call_id'] = meta_df['call_id'].astype(int) 
    meta_df['subject_id'] = meta_df['subject_id'].astype(int).astype(str) 
    meta_df['segment_number'] = meta_df['segment_number'].astype(int) 

    #Get files 
    wavs = os.path.join(sf, 'wav')
    word_time = os.path.join(sf, 'word_timing')

    if n == 0:
        for f in range(0, meta_df.shape[0]):
            #file name 
            fn = meta_df.iloc[f]['segment_id'] 
            wav_path = os.path.join(wavs, fn + '.wav')
            wt_path = os.path.join(word_time, fn + '.pkl')

            #copy wav file
            copyfile(wav_path, os.path.join(comb_wav_dir, fn+'.wav'))
            #copy word_timing file 
            copyfile(wt_path, os.path.join(comb_wt_dir, fn+'.pkl'))

        #check file names copied into "segments" folder and meta_df segment_ids 
        wav_file_names = [os.path.splitext(w)[0] for w in os.listdir(comb_wav_dir)]
        if len(set(meta_df.segment_id).difference(set(wav_file_names))) > 0:
            print('mismatched files')

        #save metadata file as starting point 
        meta_df.to_csv(os.path.join(seg_path, metadata_fn + '.csv'), index=False)
    
    else:  
        #load metadata file 
        comb_meta_df = pd.read_csv(os.path.join(seg_path, metadata_fn + '.csv'))
        comb_meta_df = comb_meta_df.sort_index() 

        #Get number of segments in combined folder 
        num_segs = comb_meta_df.shape[0]     
                
        #make mapping from original name (starting at 0) to new names (starting at #of segs) 
        seg_nums = meta_df.index.values + num_segs
        meta_df.index = seg_nums  
        meta_df['segment_id_new'] = ['ma' + str(s) for s in seg_nums]
        
        #loop over rows in metadata file 
        for f in range(0, meta_df.shape[0]):
            #original paths
            fn = meta_df.iloc[f]['segment_id'] 
            wav_path = os.path.join(wavs, fn + '.wav')
            wt_path = os.path.join(word_time, fn + '.pkl')
            # new file name 
            fn_new = meta_df.iloc[f]['segment_id_new']

            #copy/rename wav file
            copyfile(wav_path, os.path.join(comb_wav_dir, fn_new+'.wav'))
            #copy/rename word_timing file 
            copyfile(wt_path, os.path.join(comb_wt_dir, fn_new+'.pkl'))       

        #drop original name column 
        meta_df['segment_id'] = meta_df['segment_id_new']
        meta_df = meta_df.drop(['segment_id_new'], axis=1)

        #append metadata_df to combined metadata 
        comb_meta_df = pd.concat([comb_meta_df, meta_df])

        #save updated combined metadata file 
        comb_meta_df.to_csv(os.path.join(seg_path, metadata_fn + '.csv'), index=False)
