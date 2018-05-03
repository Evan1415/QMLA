#!/bin/bash
#PBS -l nodes=1:ppn=1,walltime=00:00:10


echo "Inside Global host remote script: $GLOBAL_SERVER"
host=$(hostname)
echo "host= $host"

if [[ "$host" == "node"* ]]
then

    echo "BC backend identified"
    lib_dir="/panfs/panasas01/phys/bf16951/QMD/Libraries/QML_lib"
    module load tools/redis-4.0.8
    module load languages/intel-compiler-16-u2
	SERVER_HOST=$(hostname)
	cd $lib_dir    
	redis_run_test=`python3 RedisGlobalCheck.py -g=$GLOBAL_SERVER -rqid=0 -rh=$host` 
	redis_test=$(echo $redis_run_test)	
	echo "redis test: $redis_test"

else
    echo "Neither local machine (Brian's university laptop) or blue crystal identified." 
fi


