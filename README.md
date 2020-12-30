# audio_segmentation

There are three different segmentation methods in this repository.

## Microsoft Azure Segmentation 

Microsoft Azure segmentation uses the outputs of the Microsoft Azure transcription process which includes "offset" and "durations" for each string of transcribed text. This is used to generate segment .wav files and word timing .npy files. 


## ComboSAD 

The ComboSAD algorithm. 

Original Code:  /nfs/turbo/McInnisLab/gideonjn/SegmentationScript/extractComboSAD.py 


## soheil_VAD 

Soheil's Voice Activity Detector (VAD). 

NOTE: apply_combosad.m - runs Voice Activity Detection algorithm!!! 

TO DO: 2020-12-30 HMN 
Fix the VAD segment start and stop estimation code (“apply_combosad.m”) 
Edit the matlab to only contain VAD 


