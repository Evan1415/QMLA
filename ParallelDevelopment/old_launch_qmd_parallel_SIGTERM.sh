#!/bin/bash
#PBS -l nodes=2:ppn=3,walltime=10:00:00

let NUM_WORKERS="$PBS_NUM_NODES * $PBS_NUM_PPN"
echo "Num workers: $NUM_WORKERS"

host=$(hostname)
echo "host= $host"

if [ "$host" == "IT067176" ]
then
    echo "host= $host"
    running_dir=$(pwd)
    lib_dir="/home/bf16951/Dropbox/QML_share_stateofart/QMD/Libraries/QML_lib"
    script_dir="/home/bf16951/Dropbox/QML_share_stateofart/QMD/ExperimentalSimulations"
    SERVER_HOST='localhost'
    ~/redis-4.0.8/src/redis-server & 
        
elif [[ "$host" == "newblue"* ]]
then
    echo "BC frontend identified"
    echo "host= $host"
    running_dir=$(pwd)
    lib_dir="/panfs/panasas01/phys/bf16951/QMD/Libraries/QML_lib"
    script_dir="/panfs/panasas01/phys/bf16951/QMD/ExperimentalSimulations"
    module load tools/redis-4.0.8
    module load mvapich/gcc/64/1.2.0-qlc
    echo "launching redis"
    redis-server --protected-mode no &
    SERVER_HOST='localhost'


elif [[ "$host" == "node"* ]]
then
    echo "BC backend identified"
    echo "host= $host"
    running_dir=$(pwd)
    lib_dir="/panfs/panasas01/phys/bf16951/QMD/Libraries/QML_lib"
    script_dir="/panfs/panasas01/phys/bf16951/QMD/ExperimentalSimulations"
    module load tools/redis-4.0.8
    module load languages/intel-compiler-16-u2
    SERVER_HOST=$(head -1 "$PBS_NODEFILE")
    echo "launching redis"
    redis-server --protected-mode no &


else
    echo "Neither local machine (Brian's university laptop) or blue crystal identified." 
fi

set -x
job_id=$PBS_JOBID

job_number="$(cut -d'.' -f1 <<<"$job_id")"
echo "Job id is $job_number"

# The redis server is started on the first node.
REDIS_URL=redis://$SERVER_HOST:6379
echo "REDIS_URL is $REDIS_URL"
#TODO create a redis config

mkdir -p $PBS_O_WORKDIR/logs;
echo "workers will log in $PBS_O_WORKDIR/logs"

cd $lib_dir
if [[ "$host" == "node"* ]]
then
	echo "Launching RQ worker on remote nodes using mpirun"
	mpirun -np $NUM_WORKERS rq worker -u $REDIS_URL > $PBS_O_WORKDIR/logs/worker_$job_number.log 2>&1 &
else
	echo "Launching RQ worker locally."
	rq worker -u $REDIS_URL > logs/worker_$HOSTNAME.log 2>&1 &
fi

sleep 10

cd $script_dir
python3 Exp.py -rq=1 -p=1200 -e=300 -bt=100 -pkl=0 -host=$SERVER_HOST



sleep 1
echo "   SHUTDOWN REDIS   "
redis-cli shutdown

