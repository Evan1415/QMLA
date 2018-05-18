#!/bin/bash
#PBS -l nodes=1:ppn=4,walltime=00:00:30

rm dump.rdb 

let NUM_WORKERS="$PBS_NUM_NODES * $PBS_NUM_PPN"
echo "Num workers: $NUM_WORKERS"
# echo $1

# QMD_ID=$1
let REDIS_PORT="6300 + $QMD_ID"
echo "QMD ID =$QMD_ID; REDIS_PORT=$REDIS_PORT"
echo "Global server: $GLOBAL_SERVER"
host=$(hostname)
echo "just host= $host"



if [ "$host" == "IT067176" ]
then
    echo "Brian's laptop identified"
    running_dir=$(pwd)
    lib_dir="/home/bf16951/Dropbox/QML_share_stateofart/QMD/Libraries/QML_lib"
    script_dir="/home/bf16951/Dropbox/QML_share_stateofart/QMD/ExperimentalSimulations"
    SERVER_HOST='localhost'
#    ~/redis-4.0.8/src/redis-server  $lib_dir/RedisConfig.conf & 
        
elif [[ "$host" == "newblue"* ]]
then
    echo "BC frontend identified"
    running_dir=$(pwd)
    lib_dir="/panfs/panasas01/phys/bf16951/QMD/Libraries/QML_lib"
    script_dir="/panfs/panasas01/phys/bf16951/QMD/ExperimentalSimulations"
    module load tools/redis-4.0.8
    module load mvapich/gcc/64/1.2.0-qlc
    echo "launching redis"
#   redis-server $lib_dir/RedisConfig.conf --protected-mode no  &

    SERVER_HOST='localhost'


elif [[ "$host" == "node"* ]]
then
    echo "BC backend identified"
    #running_dir="$(pwd)"
	running_dir="/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment"
    lib_dir="/panfs/panasas01/phys/bf16951/QMD/Libraries/QML_lib"
    script_dir="/panfs/panasas01/phys/bf16951/QMD/ExperimentalSimulations"
    module load tools/redis-4.0.8
    module load languages/intel-compiler-16-u2
	
    SERVER_HOST=$(head -1 "$PBS_NODEFILE")
	cd $lib_dir
	redis-server RedisDatabaseConfig.conf --protected-mode no --port $REDIS_PORT & 
	redis-cli -p $REDIS_PORT flushall
else
    echo "Neither local machine (Brian's university laptop) or blue crystal identified." 
fi

cd $lib_dir
echo "Going in to launch redis script"
echo "If this fails -- ensure permission enabled on RedisLaunch script in library"
# ./RedisLaunch.sh $GLOBAL_SERVER $REDIS_PORT &

sleep 7

set -x
job_id=$PBS_JOBID

job_number="$(cut -d'.' -f1 <<<"$job_id")"
echo "Job id is $job_number"
cd $running_dir
mkdir -p $running_dir/logs
mkdir -p $PBS_O_WORKDIR/logs


# Create the node file ---------------
# 
cat $PBS_NODEFILE
export nodes=`cat $PBS_NODEFILE`
export nnodes=`cat $PBS_NODEFILE | wc -l`
export confile=$PBS_O_WORKDIR/logs/inf.$PBS_JOBID.conf
for i in $nodes; do
 echo ${i} >>$confile
done
# -------------------------------------

echo "Nodelist"
cat $confile 

# The redis server is started on the first node.
REDIS_URL=redis://$SERVER_HOST:$REDIS_PORT
echo "REDIS_URL is $REDIS_URL"
#TODO create a redis config

echo "Running dir is $running_dir"
echo "workers will log in $running_dir/logs"
QMD_LOG="$running_dir/logs/QMD_$QMD_ID.$job_number.log"

cd $lib_dir
if [[ "$host" == "node"* ]]
then
	echo "Launching RQ worker on remote nodes using mpirun"
	mpirun -np $NUM_WORKERS -machinefile $confile rq worker $QMD_ID -u $REDIS_URL >> $PBS_O_WORKDIR/logs/worker_$job_number.log 2>&1 &
#	mpirun -np $NUM_WORKERS rq worker $QMD_ID -u $REDIS_URL > $PBS_O_WORKDIR/logs/worker_$job_number.log 2>&1 &
else
	echo "Launching RQ worker locally"
	echo "RQ launched on $REDIS_URL at $(date +%H:%M:%S)" > $running_dir/logs/worker_$HOSTNAME.log 2>&1 
	rq worker -u $REDIS_URL >> $running_dir/logs/worker_$HOSTNAME.log 2>&1 &
fi

sleep 5

cd $script_dir
# python3 Exp.py -rq=0 -p=2500 -e=400 -bt=75 -qid=$QMD_ID -pkl=0 -host=$SERVER_HOST
# python3 Exp.py -rq=1 -p=100 -e=40 -bt=25 -qid=$QMD_ID -pkl=0 -host=$SERVER_HOST
echo "Starting Exp.py at $(date +%H:%M:%S); results dir: $RESULTS_DIR"

export full_path_to_results="$script_dir/$RESULTS_DIR"

#python3 Exp.py -rq=1 -p=3000 -e=600 -bt=250 -qid=$QMD_ID -rqt=10000 -pkl=0 -host=$SERVER_HOST -port=$REDIS_PORT -dir=$RESULTS_DIR
python3 Exp.py -rq=1 -p=25 -e=4 -bt=2 -qid=$QMD_ID -rqt=10000 -pkl=0 -host=$SERVER_HOST -port=$REDIS_PORT -dir=$RESULTS_DIR -log=$QMD_LOG

# python3 Exp.py -rq=1 -p=25 -e=4 -bt=2 -qid=$QMD_ID -rqt=10000 -pkl=0 -host=$SERVER_HOST -port=$REDIS_PORT -dir=$RESULTS_dir


echo "Finished Exp.py at $(date +%H:%M:%S); results dir: $RESULTS_DIR"

sleep 1
#cd $lib_dir
#echo "Removing $QMD_ID from redis on $SERVER_HOST"
# python3 RedisManageServer.py -rh=$SERVER_HOST -rqid=$QMD_ID -action='remove'
# python3 RedisGlobalCheck.py -rh=$SERVER_HOST -rqid=$QMD_ID -g=$GLOBAL_SERVER --action='remove'
#finished=`python3 RedisGlobalCheck.py -rh=$SERVER_HOST -rqid=$QMD_ID -g=$GLOBAL_SERVER --action='check-end'`
#finished_test="$(echo $finished)"
#finished_test=""
#echo "Finished test: $finished_test"
#if [ $finished_test == "redis-finished" ]
#then
#	echo "Redis server on $SERVER_HOST no longer needed by any QMD; terminating at $(date +%H:%M:%S)."
#	redis-cli flushall
#	redis-cli -p $REDIS_PORT shutdown
#elif  [ $finished_test == "redis-running" ]
#then
#	echo "Redis server on $SERVER_HOST still in use by other QMD at $(date +%H:%M:%S)"
#else
#	echo "Neither condition met on finished_test: $finished_test"
#fi

redis-cli -p $REDIS_PORT flushall
redis-cli -p $REDIS_PORT shutdown
echo "QMD $QMD_ID Finished; end of script at Time: $(date +%H:%M:%S)"
