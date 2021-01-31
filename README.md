# audio_segmentation

There are three different segmentation methods in this repository.

## Microsoft Azure Segmentation 

Microsoft Azure segmentation uses the outputs of the Microsoft Azure transcription process which includes "offset" and "durations" for each string of transcribed text. This is used to generate segment .wav files and word timing .npy files. 

NOTE: This segmentation will result in shorter segments tight to the word boundaries. There will not be any segments with only non-verbal expressions (i.e. laughter or sighing). 


## ComboSAD 

The ComboSAD algorithm. 

Original Code:  /nfs/turbo/McInnisLab/gideonjn/SegmentationScript/extractComboSAD.py 

John Gideon Paper: https://ieeexplore.ieee.org/abstract/document/7472099 (settings listed in paper 700 ms minimum silence)

John Gideon: (Email 2021-01-22) I ultimately validated the ComboSAD algorithm using the annotated subset of the assessment calls.

#Updates/Issues:
- converted to python3 (updated LPC function to librosa) 
- added input checking 
- issues with segmenting silence instead of speech sometimes *** 
- LPC function throws "numerical error, input ill conditioned?" for some audio 
- maximum speech input parameter is used to remove bias but does not enforce maximum segment length 

ComboSAD 
SEGMENTS OF SILENCE - NOT SURE WHAT TO DO ABOUT THIS??? If anything
Test audio - works with 15 seconds, 30 seconds
1 minute - mostly selecting silences *** - different sections selected when full minute of audio passed in 
changePt - variable threshold based on bimodal GMM 
15 second (changePt = 2.04)
30 second (changePt = 2.2) 
1 minute (changePt = 4.46) 
** possibly made this dynamic for the personal calls *** 
Mood Varying Acoustic = John uses 1.8 threshold 




## soheil_VAD 

Soheil's Voice Activity Detector (VAD). 

Original Code: /nfs/turbo/McInnisLab/Soheil/personal_call_segments/combosad (NOTE: THIS IS NOT COMBOSAD!!) 
NOTE: apply_combosad.m - runs Voice Activity Detection algorithm!!! 

TO DO: 2020-12-30 HMN 
Fix the VAD segment start and stop estimation code (“apply_combosad.m”) 
Edit the matlab to only contain VAD 
