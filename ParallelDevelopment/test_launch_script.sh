#!/bin/bash


for i in `seq 1 5`;
do
	qsub -v QMD_ID=$i launch_qmd_parallel.sh.cjw
done 
