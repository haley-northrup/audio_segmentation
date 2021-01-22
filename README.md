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


## soheil_VAD 

Soheil's Voice Activity Detector (VAD). 

Original Code: /nfs/turbo/McInnisLab/Soheil/personal_call_segments/combosad (NOTE: THIS IS NOT COMBOSAD!!) 
NOTE: apply_combosad.m - runs Voice Activity Detection algorithm!!! 

TO DO: 2020-12-30 HMN 
Fix the VAD segment start and stop estimation code (“apply_combosad.m”) 
Edit the matlab to only contain VAD 
