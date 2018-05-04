#!/bin/bash

echo "local host is $(hostname). Global redis launced here." 
./global_redis_launch.sh

global_server=$(hostname)

for i in `seq 1 40`;
do
	qsub -v QMD_ID=$i,GLOBAL_SERVER=$global_server  launch_qmd_parallel.sh
done 


