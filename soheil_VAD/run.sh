#!/bin/sh
#SBATCH --job-name=segmenation_with_start_end_times
#SBATCH --mail-user=ndbhagwa@umich.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --export=ALL
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=24:00:00
#SBATCH --mem=3500mb
#SBATCH --account=emilykmp1
#SBATCH --partition=standard
#SBATCH --array 1-1000
#SBATCH --output=log/output${SLURM_ARRAY_TASK_ID}.log

module load matlab
#cd /nfs/turbo/McInnisLab/ndbhagwa/combosad
matlab -r "doSegmentationAll(${SLURM_ARRAY_TASK_ID}, 1000); quit;"
