#!/bin/sh
#SBATCH --job-name=stitch_v3
#SBATCH --mail-user=hnorthru@umich.edu
#SBATCH --mail-type=FAIL
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=75000
#SBATCH --time=6:00:00
#SBATCH --array=1-100
#SBATCH --output=logs/%x-%j.log
#SBATCH --account=emilykmp1
#SBATCH --partition=standard
#SBATCH --export=NONE 

source /home/hnorthru/anaconda3/etc/profile.d/conda.sh 
conda activate audio_proc_20210115

python stitch_audio_PRIORI_V3.py \
--job_num=$SLURM_ARRAY_TASK_ID   \
--metadata_path='/nfs/turbo/McInnisLab/priori_v3_data_Dec_2020/tables/call_audio.csv' \
--output_dir='/scratch/emilykmp_root/emilykmp/hnorthru/priori_v3_data_Dec_2020/call_audio_stitched/' \