#!/bin/bash 
#####SBATCH --job-name=priori_ms_gen_segs
#####SBATCH --mail-user=hnorthru@umich.edu
#####SBATCH --mail-type=FAIL
#####SBATCH --nodes=1
#####SBATCH --ntasks-per-node=1
#####SBATCH --mem=10000
#####SBATCH --time=06:00:00
#####SBATCH --array 1
#####SBATCH --output=logs/%x-%j.log
#####SBATCH --account=emilykmp1
#####SBATCH --partition=standard
#####SBATCH --export=NONE


python gen_microsoft_segments_from_ASR_output.py \
--ms_asr_output_files='/nfs/turbo/McInnisLab/hnorthru/code/kmatton/Feature-Extraction/temp/pv1_1250001_set0.txt' \
--output_dir='./temp_audio' \
--wav_dir='/nfs/turbo/McInnisLab/priori_v1_data/call_audio/speech/' \
--call_metadata='/nfs/turbo/McInnisLab/hnorthru/code/kmatton/Feature-Extraction/temp/priori_v1_call_metadata.csv' \