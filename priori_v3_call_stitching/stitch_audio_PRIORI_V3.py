''' Call Stitching for PRIORI V3 

NOTE: All .wav files are not able to be loaded
Track whether a .wav file is used to create a stitched call 
DOES NOT SAVE CALLS LENGTH == 0!

PRIORI V3 Raw Audio Sample Rate = 16kHz 

''' 
from scipy.io import wavfile
import librosa
import os
import pandas as pd
import numpy as np
import math 
import argparse 
from IPython import embed 


SAMPLE_RATE = 16000 #Hz  PRIORI_V3 raw audio sample rate 


def chunks(l, n_chunks):
	n_in_chunk = math.ceil(float(len(l))/float(n_chunks))
	for i in range(0,len(l),n_in_chunk):
		yield l[i:i+n_in_chunk]

def stitch_audio_priori_v3(args): 
    """
    Stitch priori v3 call parts into one .wav file per call  

    :param args: input arguments from argparse 
    :return: none
    """

    #make output directories 
    output_wav = os.path.join(args.output_dir, 'wav') 
    output_meta = os.path.join(args.output_dir, 'metadata')
    #if not os.path.exists(output_wav): 
    #    os.makedirs(output_wav) 
    #if not os.path.exists(output_meta): 
    #    os.makedirs(output_meta) 

    #set up 
    call_part_df = pd.read_csv(args.metadata_path)
    wav_num = [f.split('/')[-1].split('.wav')[0] for f in call_part_df['file_path'].values]
    call_part_df['wav_number'] = np.array(wav_num).astype(int) #add wav number field 

    #get call_ids in chunk
    chunk = int(args.job_num)
    call_ids = sorted(call_part_df['call_id'].unique()) 
    call_ids = list(chunks(call_ids,100))[chunk-1] 

    print('Calls in chunk: ')
    print(len(call_ids))  

    # Stitch Calls 
    #******************************************************************
    print('stitching calls...') 
    
    #Iterate over calls
    row = 0 
    for c in call_ids:
        print('call_id: ' + c)
        cidx = call_part_df['call_id'] == c
        call_df = call_part_df.loc[cidx, :]
        call_df = call_df.sort_values(by=['wav_number'])
        files = call_df['file_path'].values 
        
        #Stitch call parts together 
        audio = []
        print('num wavs:' + str(len(files)))
        call_df['stitched'] = False
        for f in files:
            try:
                #load .wav file 
                a, Fs = librosa.load(f, SAMPLE_RATE)
                #using .extend to stitch together all wavfiles making up a single call
                audio.extend(a) 
                print('loaded: ' + str(f))
                call_df.loc[call_df['file_path'] == f, 'stitched'] = True 
            except Exception as e:
                print('could not load file: ' + str(f)) 

        #Save stitched call
        ## convert wavform data to int16 with vals between -32768 +32768. 
        ## Librosa writes wavform data to float with vals -1 +1  
        if len(audio) > 0:
            audio = np.array(audio) 
            audio = (audio * 32767).astype('int16')
            stitched_path = os.path.join(output_wav, c+'.wav')
            wavfile.write(stitched_path, Fs, audio)

        #Save metadata
        #************************
        call_df.to_csv(os.path.join(output_meta, c+'.csv'), index=False)

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job_num', type=int, default=1) 
    parser.add_argument('--output_dir', type=str, help="Path to directory to output feature files to.")
    parser.add_argument('--metadata_path', type=str, help="Path to segment metadata file (subject, call, etc.).") 
    return parser.parse_args()

    
def main():
    args = _parse_args() 
    stitch_audio_priori_v3(args) 

if __name__ == '__main__': 
    main() 
