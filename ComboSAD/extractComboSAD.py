import sys, os
#print(sys.executable)
import numpy as np
import scipy.io.wavfile as wav
from scipy.signal import medfilt, lfilter
from scipy.cluster.vq import kmeans
from sklearn.decomposition import PCA 
from resampy import resample 
from librosa import lpc 
from IPython import embed

#DEBUG 
#import matplotlib.pyplot as plt
#import librosa
#import librosa.display 

#def plot_mel_spec(x, name):
#    sr = 16000
#    S = librosa.feature.melspectrogram(y=x, sr=sr)
#    fig, ax = plt.subplots()
#    S_dB = librosa.power_to_db(S, ref=np.max)
#    img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, ax=ax)
#    fig.colorbar(img, ax=ax, format='%+2.0f dB')
#    ax.set(title='Mel-frequency spectrogram')
#    fig.savefig(name + '.png')


# Get Mel Filterbank - https://github.com/jameslyons/python_speech_features
def hz2mel(hz):
    return 2595 * np.log10(1+hz/700.)
def mel2hz(mel):
    return 700*(10**(mel/2595.0)-1)
def get_filterbanks(nfilt=20,nfft=512,samplerate=16000,lowfreq=0,highfreq=None):
    highfreq= highfreq or samplerate/2
    assert highfreq <= samplerate/2, "highfreq is greater than samplerate/2"

    # compute points evenly spaced in mels
    lowmel = hz2mel(lowfreq)
    highmel = hz2mel(highfreq)
    melpoints = np.linspace(lowmel,highmel,nfilt+2)
    # our points are in Hz, but we use fft bins, so we have to convert
    #  from Hz to fft bin number
    bin = np.floor((nfft+1)*mel2hz(melpoints)/samplerate)

    fbank = np.zeros([nfilt,nfft//2+1])
    for j in range(0,nfilt):
        for i in range(int(bin[j]), int(bin[j+1])):
            fbank[j,i] = (i - bin[j]) / (bin[j+1]-bin[j])
        for i in range(int(bin[j+1]), int(bin[j+2])):
            fbank[j,i] = (bin[j+2]-i) / (bin[j+2]-bin[j+1])
    return fbank

# Find and remove the DC component of a signal
def removeNoiseBias(signal, windowSize, stepSize):

    if stepSize == 0:
        raise Exception("removeNoiseBias: stepSize must be greater than 0")

    # Pad with first and last value on both ends (windowSize/2 length)
    outSignal = signal
    outSignal = np.pad(outSignal, int(windowSize/2), 'median', stat_length= int(windowSize/2))

    # Pad end until even number of frames
    nPad = int(stepSize - (len(outSignal) % stepSize))
    outSignal = np.pad(outSignal, (0, nPad), 'edge')

    # Setup framing
    nFrames = int(((len(outSignal) - windowSize) / stepSize) + 1)  

    # Get percentile signal
    frameStart = 0
    prctSignal = np.empty((nFrames,))
    #for fOn in xrange(nFrames):
    for fOn in range(nFrames):
        # Get frame
        frame = outSignal[frameStart:frameStart+windowSize]
        frameStart = frameStart + stepSize
        prctSignal[fOn] = np.percentile(frame, 1)

    # Remove bias
    prctSignal = resample(prctSignal, 1, stepSize)
    prctSignal = prctSignal[:len(signal)]
    return signal - prctSignal

# Find the midpoint between two Guassians
def findBimodalChangePoint(data, totalIter, kmeansMaxIter):
    candidates = np.empty((totalIter,))
    #for it in xrange(totalIter):
    for it in range(totalIter):
        C, _ = kmeans(data, 2, kmeansMaxIter)
        candidates[it] = np.mean(C)
    return np.median(candidates)

# Reference:
#        Sadjadi, Seyed Omid, and John HL Hansen. "Unsupervised speech activity 
#        detection using voicing measures and perceptual spectral flux." Signal 
#        Processing Letters, IEEE 20.3 (2013): 197-200.
def extractComboSAD(origAudio, Fs, minSpeechSec=2.0, minSilenceSec=0.8, maxSpeechSec=30.0):
    ### EXTRACT COMBOSAD SIGNAL ###

    #Check Input 
    if minSpeechSec <= 0  or minSpeechSec == None:
        raise Exception("minSpeechSec must be float greater than 0")
    if maxSpeechSec == None or maxSpeechSec <= 0:
        raise Exception("maxSpeechSec must be a float greater than 0")
    if minSilenceSec == None or minSilenceSec <= 0:
        raise Exception("minSilenceSec must be a float greater than 0")
    # Check audio length and amplitude 
    if len(origAudio)==0:
        return []
    if len(origAudio)/Fs < minSpeechSec:
        print('Audio length less than minSpeechSec')
        return []
    if origAudio.sum() == 0:
        print('Audio amplitude all zeros')
        return []
 
    # Setup constants
    windowSize = int(round(0.032*Fs))
    stepSize = int(round(0.010*Fs))
    Fss = Fs / stepSize
    minPitchLag = int(round(0.002*Fs))
    maxPitchLag = int(round(0.016*Fs))
    hannWindow = np.hanning(windowSize)
    hammWindow = np.hamming(windowSize)
    nfft = 2048
    freq = (Fs/2)*np.linspace(0,1,int(nfft/2)+1,endpoint=True)
    prevXm = np.full((80,), np.nan)
    mfBank = get_filterbanks(80,nfft,Fs)
    Pf = np.arange(62.5, 501, 62.5)

    # Subtract mean and remove sudden spikes
    audio = origAudio - np.mean(origAudio)
    audio = medfilt(audio,3)

    # Pad with edge value on both ends
    audio = np.pad(audio, int(windowSize/2), 'edge')

    # Pad end until even number of frames
    #nPad = int(stepSize - (len(audio) % stepSize))
    nPad = int(stepSize - (len(audio) - windowSize)% stepSize)
    audio = np.pad(audio, (0, nPad), 'edge')

    # Setup framing
    nFrames = ((len(audio) - windowSize) / stepSize) + 1    
    nFrames = int(nFrames)
    nFeats = 6
    feats = np.full((nFrames, nFeats), np.nan)

    # Loop through frames
    frameStart = 0
    ill_cond_ct = 0
    #for fOn in xrange(nFrames):
    for fOn in range(nFrames):
        # Get frame
        frame = audio[frameStart:frameStart+windowSize]
        frameStart = frameStart + stepSize
        x = frame * hannWindow;

        # Deal with constant signal
        if np.all(x==x[0]):
            continue

        # Autocorrelation (A) - Different from paper (Normalize by maximum
        #       potential autocorrelation without window)
        rxx = np.empty((maxPitchLag,))
        #for i in xrange(maxPitchLag):
        for i in range(maxPitchLag):
            denom = np.sum(np.maximum(np.square(x[i:]), np.square(x[:windowSize-i])))
            rxx[i] = np.matmul(x[i:].T, x[:windowSize-i]) / denom
        rxx = rxx * np.sum(np.square(x))
        rxx_0 = rxx[0]

        # Check for autocorrelation error
        if np.all(rxx[minPitchLag:] <= rxx_0):
            # Harmonicity (A1)
            rxx_max = np.max(rxx[minPitchLag:])
            feats[fOn,0] = rxx_max / (rxx_0 - rxx_max)

            # Clarity (A2)
            D_func = np.sqrt(2*(rxx_0-rxx[minPitchLag:]))
            feats[fOn,1] = 1 - (np.min(D_func)/np.max(D_func))

            # Prediction Gain (A3) 
            #some frames throw ill conditioned error
            try:
                #a, _, _ = lpc(x,10)
                a = lpc(x, 10)
                a = np.pad(a[1:], (1,0), 'constant')
                est_x = lfilter(a,1,x)
                resErr = np.sum(np.abs(x-est_x))
                feats[fOn,2] = np.log(rxx_0/resErr)
            except Exception as e: #keep track of frames that are "ill conditioned" (likely noise or no speech) 
                ill_cond_ct = ill_cond_ct + 1

        # STFT
        X = np.abs(np.fft.fft(frame * hammWindow, nfft))
        X = X[:int((nfft/2)+1)]

        # Periodicity (B1)
        P = np.empty(len(Pf),)
        for i, w in enumerate(Pf):
            Pw = np.empty((8,))
            #for j in xrange(8):
            for j in range(8):
                Pw[j] = np.log(X[np.argmin(np.abs(freq-(w*(j+1))))])
            P[i] = np.sum(Pw)
        feats[fOn,3] = np.max(P)
        
        # Perceptual Spectral Flux (B2)
        Xm = np.matmul(X, mfBank.T)
        Xm = Xm / np.sum(np.square(Xm)) # Energy Normalized
        feats[fOn,4] = -np.linalg.norm(Xm-prevXm, 1)   
        prevXm = Xm;

        # RMS Energy (Added in addition to paper)
        feats[fOn,5] = np.sqrt(np.mean(np.square(x)))

    #Track ill conditioned frames 
    print('ill conditioned count: ' + str(ill_cond_ct)) 
    print('nFrames: ' + str(nFrames))
    print(ill_cond_ct/nFrames)

    # Set all skipped frames to minimum
    minVec = np.nanmin(feats, axis=0)
    indices = np.argwhere(np.isnan(feats))
    for idx in indices:
        feats[idx[0],idx[1]] = minVec[idx[1]]

    # Normalize
    meanVec = np.mean(feats,0)
    stdVec = np.std(feats,0)
    feats = (feats - meanVec) / stdVec

    # PCA to get comboSAD signal
    try:
        pca = PCA(n_components=1)
        pca.fit(feats)
        comboSAD = pca.transform(feats)[:,0]
    except:
        return []
    comboSAD = np.real(comboSAD)

    ### FORM CONTIGUOUS SEGMENTS ###

    # Setup constants
    minSpeech = int(round(minSpeechSec*Fss))
    minSilence = int(round(minSilenceSec*Fss))
    maxContSpeech = int(round(maxSpeechSec*Fss)) # Used as window to remove noise bias

    # Smooth with median filter to remove spikes
    smSAD = medfilt(comboSAD,7)
    
    # Remove baseline bias by subtracting the 1st percentile in sliding window
    smSAD = removeNoiseBias(smSAD, maxContSpeech, minSpeech)

    # Smooth with hanning window to remove small silences between words
    hannWindowSil = np.hanning(int(round(minSpeech/2)))
    smSAD = np.convolve(smSAD, hannWindowSil, 'same') / np.sum(hannWindowSil)

    # Fit with bimodal GMM and get change point
    changePt = findBimodalChangePoint(smSAD, 10, 1000)

    # Get binary segmentation signal
    smSAD = (smSAD>=changePt).astype(np.int)
    print(changePt) 

    # Convert to segments
    smSAD = np.pad(np.diff(smSAD), (1,0), 'constant', constant_values=smSAD[0])
    starts = np.where(smSAD==1)[0]
    stops = np.where(smSAD==-1)[0]
    if len(stops) < len(starts):
        stops = np.pad(stops, (0,1), 'constant', constant_values=len(smSAD))
    segTimes = [{'start': x, 'stop': y} for x,y in zip(starts, stops)]

    # Remove min silences
    silOn = 0
    while silOn < len(segTimes)-1:
        if segTimes[silOn+1]['start'] - segTimes[silOn]['stop'] <= minSilence:
            # Merge segments
            segTimes[silOn]['stop'] = segTimes[silOn+1]['stop']
            del segTimes[silOn+1]
        else:
            silOn += 1

    # Remove min speech
    starts = np.array([x['start'] for x in segTimes])
    stops = np.array([x['stop'] for x in segTimes])
    segFilter = (stops-starts) > minSpeech
    starts = starts[segFilter]
    stops = stops[segFilter]
    
    # Resample times
    starts = np.round(starts*stepSize)
    stops = np.round(stops*stepSize)
    starts = np.maximum(starts, 0)
    stops = np.maximum(stops, 0)
    starts = np.minimum(starts, len(origAudio))
    stops = np.minimum(stops, len(origAudio))

    # Get segments
    return [{'Segment': origAudio[x:y], 'Start': x, 'Stop': y} for x,y in zip(starts, stops)]

def unitTest():
    wavPath = '/nfs/turbo/McInnisLab/priori_v1_data/call_audio/assessment_speech/10006.wav'
    (Fs, audio) = wav.read(wavPath)
    print('Audio is '+str((len(audio)/Fs)/60)+' minutes long')
    useLen = np.min([len(audio), Fs*180])#120
    audio = audio[:useLen]
    print('Using '+str((useLen/Fs)/60)+' minute subset')
    print('Extracting segments using ComboSAD and default parameters')
    segments = extractComboSAD(audio, Fs, minSpeechSec=1.0, minSilenceSec=0.7, maxSpeechSec=30.0)
    for count, segment in enumerate(segments):
        print('Segment '+str(count)+':')
        print(str(segment['Start']) + ' - ' + str(segment['Stop']))
        print(str(segment['Start']/Fs) + ' - ' + str(segment['Stop']/Fs))
        print('   ' + str(np.sqrt(np.mean(np.square(segment['Segment'])))) + ' RMS Energy')

        #SAVE TEST 
        wav.write(str(count) +'_test.wav', Fs, segment['Segment'])


if __name__ == "__main__":
    unitTest()
