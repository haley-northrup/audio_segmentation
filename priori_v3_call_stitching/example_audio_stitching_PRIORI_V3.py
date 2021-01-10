''' Call Stitching for PRIORI V3 

Original Code Provided by Steve Anderau (2020-12-23) 

''' 

import extractComboSAD as sad
from scipy.io import wavfile
import librosa
import os
import pandas as pd
import numpy as np

wavnum = []
filesInFolder = []

## Loop through wave files in folder and sort the filenames in incrementing integers
for f in os.listdir(folder):
    wavnum.append(int(f.split('.wav')[0]))
    filesInFolder.append(os.path.join(folder,f))
order = np.argsort(wavnum)
files = np.array(filesInFolder)[order]
del order
audio = []

## Read wavfiles and downsample to 8khz
for w in files:
    try:
        a, s = librosa.load(w, sr=8000)
        #using .extend to stitch together all wavfiles making up a single call
        audio.extend(a)
    except Exception as e: print(e)
del files
length = len(audio)/float(Fs)
print(length)
if length < 3600.0:
    try:
        ## convert wavform data to int16 with vals between -32768 +32768. this makes the wavform data usable by comboSAD 
        ## Librosa writes wavform data to float with vals -1 +1  
        audio = (a * 32767).astype('int16')
        comSad = sad.extractComboSAD(audio, Fs)
        for seg_part, seg in enumerate(comSad):
            if not os.path.exists(segPath):
                os.makedirs(segPath)
            speechAudio = seg['Segment']
            length = (len(speechAudio))/float(Fs)
            segName = "part" + str(seg_part) + "_" + str(length) + ".wav"
            path = os.path.join(segPath, segName)
            print('segment %d of length %.2f seconds processed' % (seg_part, length))
            wavfile.write(path, Fs, speechAudio)
    except Exception as e: print(e)
