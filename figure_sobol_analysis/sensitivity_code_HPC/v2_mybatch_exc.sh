#!/bin/bash

#SBATCH --ntasks=2
#SBATCH --mem=16GB


#SBATCH -J BluePyOpt_IPP
#SBATCH -p costas
#SBATCH -t 96:00:00
#SBATCH --array=0-300

##SBATCH --output=/dev/null --error=/dev/null

source /home/wuy2/2023_0111_bpo_mod/venv_mod_bpo/bin/activate

# python data_compilation.py ~/2023_1009_exc_mod4/  ${SLURM_ARRAY_TASK_ID} 
python data_compilation_r2.py ~/2023_1009_exc_mod4/ ${SLURM_ARRAY_TASK_ID} 
# python data_compilation_r4_no_sort.py ~/2023_1009_exc_mod4/ ${SLURM_ARRAY_TASK_ID} 