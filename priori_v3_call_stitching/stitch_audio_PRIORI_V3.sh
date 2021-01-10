#!/bin/sh
#SBATCH --job-name=stitch_v3
#SBATCH --mail-user=hnorthru@umich.edu
#SBATCH --mail-type=FAIL
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=50000
#SBATCH --time=24:00:00
#SBATCH --array=1-100
#SBATCH --output=logs/%x-%j.log
#SBATCH --account=emilykmp1
#SBATCH --partition=standard
#SBATCH --export=NONE 

source /nfs/turbo/McInnisLab/hnorthru/anaconda3/etc/profile.d/conda.sh 
conda activate gid_8_tn_20200220

python stitch_audio_PRIORI_V3.py \
--job_num=$SLURM_ARRAY_TASK_ID   \
--output_dir='/nfs/turbo/McInnisLab/priori_v3_data_Dec_2020/call_audio_stitched/' \
--metadata_path='/nfs/turbo/McInnisLab/priori_v3_data_Dec_2020/tables/call_audio.csv' \
