## soheil_VAD 

Soheil's Voice Activity Detector (VAD). 

NOTE: apply_combosad.m - runs Voice Activity Detection algorithm!!! 

NOTE: Error in computation of start and end of segments!!! - see note below. 

Soheil_VAD:SEGMENTS 
Original Code location: (/nfs/turbo/McInnisLab/soheil-segmentation-script) 

Run.sh → doSegmentationAll.m → apply_combosad.m 
apply_combosad.m 
Line 6: defines max section length to be 5 minutes (300 seconds) 
The start and end samples to get “sam_8k” which is at most 5 min

Segment filtering 
See functions “remove_small_” in “others” folder 

START AND END OF SEGMENTS: 
Start and end indices are computed relative to the “sam_8k” variable not the full call 
Save values of “start” and “end” in seconds
