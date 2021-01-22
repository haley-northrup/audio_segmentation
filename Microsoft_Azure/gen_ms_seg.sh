#!/bin/bash 
#SBATCH --job-name=priori_ms_gen_segs
#SBATCH --mail-user=hnorthru@umich.edu
#SBATCH --mail-type=FAIL
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=10000
#SBATCH --time=48:00:00
#SBATCH --array 1
#SBATCH --output=logs/%x-%j.log
#SBATCH --account=emilykmp1
#SBATCH --partition=standard
#SBATCH --export=NONE

source /home/hnorthru/anaconda3/etc/profile.d/conda.sh 
conda activate audio_proc_20210115

python gen_microsoft_segments_from_ASR_output.py \
--ms_asr_output_files='/nfs/turbo/chai-health/hnorthru/code/audio_segmentation/Microsoft_Azure/TEMP_test_set_path.txt' \
--output_dir='/scratch/emilykmp_root/emilykmp/hnorthru/priori_v3_data_Dec_2020/segments/' \
--wav_dir='/scratch/emilykmp_root/emilykmp/hnorthru/priori_v3_data_Dec_2020/call_audio_stitched/wav/' \
--call_metadata='/nfs/turbo/McInnisLab/priori_v3_data_Dec_2020/tables/call_audio_stitched.csv' \
