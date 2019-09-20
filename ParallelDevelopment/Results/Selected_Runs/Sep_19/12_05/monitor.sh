 

#!/bin/bash

echo "inside monitor script."
IFS=$'\n' read -d '' -r -a job_ids_s < /panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_19/12_05/job_ids_started.txt
num_jobs_started=${#job_ids_s[@]}

IFS=$'\n' read -d '' -r -a job_ids_c < /panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_19/12_05/job_ids_completed.txt
num_jobs_complete=${#job_ids_c[@]}

for k in ${job_ids_c[@]}
do
	echo $k
done


echo "num jobs started/finished: $num_jobs_started $num_jobs_complete"

while (( $num_jobs_complete < 50 ))
do
	IFS=$'\n' read -d '' -r -a job_ids_s < /panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_19/12_05/job_ids_started.txt
	num_jobs_started=${#job_ids_s[@]}

	IFS=$'\n' read -d '' -r -a job_ids_c < /panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_19/12_05/job_ids_completed.txt
	num_jobs_complete=${#job_ids_c[@]}

	echo "Waiting. Currently $num_jobs_complete / $num_jobs_started "
	sleep 3
done

sh /panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_19/12_05/FINALISE_NV-exp-method-sim__probe-with-phase__different-probe__reduced-true-mod.sh

