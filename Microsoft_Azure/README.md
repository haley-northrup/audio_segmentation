
# Microsoft Azure Segmentation 

Microsoft Azure segmentation uses the outputs of the Microsoft Azure transcription process which includes "offset" and "durations" for each string of transcribed text. This is used to generate segment .wav files and word timing .npy files. 

Library Requirements:
  * *pydub*
  * shutil 
  * os
  * numpy 
  * pickle
  * pandas 

### 0. Generate a text file with Microsoft Azure transcription output paths 

see get_ma_pv1_set_paths.py and ma_pv1_set_paths.txt as an example 

### 1. To generate segments: gen_ms_seg.sh (calls gen_microsoft_segments_from_ASR_output.py)  

NOTE: Recommend running multiple jobs and then combining outputs into single set of segments. 

OUTPUTS:
segment metdata csv file  
/wav 
/word_timing 

* 1A)  CHECK SEGMENTATION OUTPUTS (check_segmentation_output.py) * 

### 2. If genertated segments with multiple jobs, combine segment output folders to single folder and meta data file with combine_segment_job_outputs.sh (calls combine_segment_job_outputs.py) 

* 2A) CHECK SEGMENTATION OUTPUTS (check_segmentation_output.py) *


