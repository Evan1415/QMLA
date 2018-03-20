#!/bin/bash

#PBS -l nodes=1:ppn=1
#PBS -q short
#PBS -N exp_ham_eval
#PBS -o exp_ham_eval

cd $PBS_O_WORKDIR
time python3 eval.py -tests=100 -p=True -max=12 -m='Cluster_Backend'