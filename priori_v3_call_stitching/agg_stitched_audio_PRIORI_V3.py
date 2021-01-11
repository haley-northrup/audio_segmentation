import os 
import pandas as pd 
import argparse
import numpy as np 
from IPython import embed 


#Parse Arguments 
#**********************
parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', type=str, help="Path to directory with individual output files")
parser.add_argument('--wav_dir', type=str, help="Path to directory with individual wav files")
parser.add_argument('--meta_path', type=str, help="Path to directory with Priori V3 original .wav metadata")
parser.add_argument('--output_dir', type=str, help="Path to directory to output combined files to.")
args = parser.parse_args()

#Load metadata 
meta_df = pd.read_csv(args.meta_path) 

#Aggregate individual files in input_dir 
#***********************************
files = os.listdir(args.input_dir)
raw_wav_df = pd.DataFrame()
call_df = pd.DataFrame(index=meta_df['call_id'].unique())
for f in files: #each call has a file 
    #All .wavs df  
    df = pd.read_csv(os.path.join(args.input_dir, f))
    call_id = df['call_id'].unique()[0] 
    df['call_wav_count'] = df.shape[0] #number of .wav files     
    # 'stitched' refered to .wav file readable, but was not saved as full call .wav if len == 0 
    if os.path.exists(os.path.join(args.wav_dir, call_id+'.wav')):
        call_file_path = os.path.join(args.wav_dir, call_id+'.wav')
    else:
        call_file_path = np.nan 
        df['stitched'] = False 
    raw_wav_df = raw_wav_df.append(df, sort=True) 

    #Calls df 
    call_df.loc[call_id, 'total_wav_count'] = df.shape[0] #number of .wav files 
    call_df.loc[call_id, 'stitched_wav_count'] = df['stitched'].sum() #number of stitched .wav files 
    call_df.loc[call_id, 'record_id'] = df['record_id'].unique()[0]
    call_df.loc[call_id, 'is_assessment_call'] = df['is_assessment_call'].unique()[0]
    call_df.loc[call_id, 'length_seconds'] = df['length_seconds'].sum() 
    call_df.loc[call_id, 'file_path'] = call_file_path
    
#Save files
#all .wav files  
raw_wav_df.to_csv(os.path.join(args.output_dir, 'call_audio_expanded.csv'), index=False) 
#call metadata 
call_df['call_id'] = call_df.index
call_df = call_df.set_index('call_id')
call_df = call_df.reset_index()
call_df.to_csv(os.path.join(args.output_dir, 'call_audio_stitched.csv'), index=False) 