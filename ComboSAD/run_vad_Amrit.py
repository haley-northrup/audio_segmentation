import sys
import zipfile
import os
import math
import numpy as np
import pandas as pd 
from multiprocessing import Pool
import scipy.io.wavfile as wav
from extractComboSAD import extractComboSAD

def get_silences():

    inputs_dir = '/home/aromana/projects/hd/data/gfp/44k/'
    files = os.listdir(inputs_dir) 
    #files = [f for f in files if f.endswith('.wav')]
    files = ["44574.wav", "81392.wav"]

    outputs_dir = '/home/aromana/projects/hd/features/silence_timings_rerun'
    
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir) 
    
    for input_f in files: 
        output_path = os.path.join(outputs_dir , input_f.replace('.wav','.csv'))
    
        # identify speech times
        try:
            Fs, audio = wav.read(os.path.join(inputs_dir, input_f))
        except:
            print('couldnt read %s' %input_f)
            return
        #audio = audio.astype('int16')
        #print(Fs)
        #print(audio)
        
        #try:
        
        chunks = extractComboSAD(audio, Fs, minSpeechSec=0.1, minSilenceSec=0.05)
        print(chunks)
        #except:
        #    chunks = []
        #    print('error in input: %s' % input_f) 

        #print(chunks)
        #return    
        # print to a df
        
        speaking_times = pd.DataFrame(columns=['start', 'end'])
        i = 0
        for chunk in enumerate(chunks):
            chunk_start = float(chunk[1][0])/float(Fs)
            print(chunk_start)
            chunk_end = float(chunk[1][1])/float(Fs)
            print(chunk_end)
            speaking_times.loc[i] = {'start': chunk_start, 'end': chunk_end}
            i += 1
        
        speaking_times = speaking_times[['start', 'end']]
        print(speaking_times)
        speaking_times.to_csv(output_path, sep=';')
        print("finished %s" %output_path)

    return
        
if __name__== "__main__":
    get_silences()
