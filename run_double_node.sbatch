#!/bin/bash
#SBATCH --job-name=shmembench_remote
#SBATCH --output=shmembench_remote_%J.log
#SBATCH --error=shmembench_remote_err_%J.log
#SBATCH --partition=nocona        
#SBATCH --exclusive               
#SBATCH --nodes=2
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1         

module load gcc python
WORK_DIR="/lustre/scratch/$USER/$SLURM_JOB_ID"
mkdir -p $WORK_DIR 
cp -r ./deps.sh $WORK_DIR

cd $WORK_DIR
./deps.sh

source activate
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"$WORK_DIR/install/lib" python3 install/bin/compare.py




