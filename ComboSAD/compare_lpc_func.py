
import numpy as np
import librosa 
from IPython import embed 
from scikits_talkbox_lpc import lpc_ref, levinson_1d



order = 2

y, sr = librosa.load(librosa.ex('trumpet'), duration=0.020)

#LIBROSA 
a = librosa.lpc(y, order)
print('librosa') 
print(a) 

a, _, _ = lpc_ref(y, order)
print('scikits.talkbox lpc_ref') 
print(a) 


a, e, k = levinson_1d(y, order)
print('scikits.talkbox levinson_1d') 
print(a) 