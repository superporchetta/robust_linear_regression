#!/bin/bash
#SBATCH --chdir /home/troiani/
#SBATCH --nodes 1
#SBATCH --tasks-per-node 36
#SBATCH --mem 120G
#SBATCH --time 00:20:00
#SBATCH -o output.out
#SBATCH -e error.out
#SBATCH --partition=parallel

module load gcc
module load mvapich2
module load python/3.7.7

source venv/troiani/bin/activate

cd robust_linear_regression
srun python cluster_version_huber_lambda_opt.py 0.3 0.1 .5

deactivate
