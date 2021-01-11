#!/bin/sh
#SBATCH --job-name=agg_stitch
#SBATCH --mail-user=hnorthru@umich.edu
#SBATCH --mail-type=FAIL
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=10000
#SBATCH --time=2:00:00
#SBATCH --array=1
#SBATCH --output=logs/%x-%j.log
#SBATCH --account=emilykmp1
#SBATCH --partition=standard
#SBATCH --export=NONE 

source /nfs/turbo/McInnisLab/hnorthru/anaconda3/etc/profile.d/conda.sh 
conda activate gid_8_tn_20200220

python3 agg_stitched_audio_PRIORI_V3.py \
--input_dir='/nfs/turbo/McInnisLab/priori_v3_data_Dec_2020/call_audio_stitched/metadata/' \
--wav_dir='/nfs/turbo/McInnisLab/priori_v3_data_Dec_2020/call_audio_stitched/wav/' \
--meta_path='/nfs/turbo/McInnisLab/priori_v3_data_Dec_2020/tables/call_audio.csv' \
--output_dir='/nfs/turbo/McInnisLab/priori_v3_data_Dec_2020/tables/' \