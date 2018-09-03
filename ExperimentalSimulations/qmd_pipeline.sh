#!/bin/bash

test_description="QHL, non-Gaussian 5000prt;1500exp"
num_tests=1
let max_qmd_id="$num_tests"

day_time=$(date +%b_%d/%H_%M)
directory="$day_time/"

cwd=$(pwd)
long_dir="$cwd/Results/$day_time/"
bcsv="cumulative.csv"
bayes_csv="$long_dir$bcsv"

this_log="$long_dir/qmd.log"

# rm -r $long_dir
# rm $this_log
mkdir -p $long_dir
#mkdir -p $directory

"""
declare -a qhl_operators=(
'xTiPPzTiPPyTiPPzTzPPxTxPPyTyPPxTyPPyTzPPxTz' 
)
"""
declare -a qhl_operators=(
'z'
)

true_operator='xTiPPyTiPPzTiPPxTxPPyTyPPzTz'
qhl_test=0
q_id=0
exp_data=1
use_rq=0
prt=400
exp=100
if (($prt > 50))
then
    use_rq=1
fi

if (($exp > 10))
then
    use_rq=1
fi

let bt="$exp-1"
pgh=0.1
ra=0.8
rt=0.5
gaussian=1
custom_prior=1
dataset='NVB_HahnPeaks_Newdata'
#dataset='NV05_HahnPeaks_expdataset'
data_max_time=5000 # nanoseconds
data_time_offset=205 # nanoseconds


printf "$day_time: \t $test_description \n" >> QMD_Results_directories.log

if [ "$qhl_test" == 1 ]
then
    for op in "${qhl_operators[@]}";
    do
        for i in `seq 1 $max_qmd_id`;
        do
            let num_prt="$i+10"
            redis-cli flushall
            let q_id="$q_id+1"
            python3 Exp.py -p=$prt -e=$exp -bt=$bt -rq=$use_rq  -g=$gaussian -qhl=$qhl_test -ra=$ra -rt=$rt -pgh=$pgh -op=$true_operator -dir=$long_dir -qid=$q_id -pt=1 -pkl=1 -log=$this_log -cb=$bayes_csv -exp=$exp_data -cpr=$custom_prior -ds=$dataset -dst=$data_max_time -dto=$data_time_offset
        done 
    done

else
    for i in `seq 1 $max_qmd_id`;
    do
        redis-cli flushall
        let q_id="$q_id+1"
        python3 Exp.py -op=$true_operator -p=$prt -e=$exp -bt=$bt -rq=$use_rq -g=$gaussian -qhl=$qhl_test -ra=$ra -rt=$rt -pgh=$pgh -dir=$long_dir -qid=$q_id -pt=1 -pkl=1 -log=$this_log -cb=$bayes_csv -exp=$exp_data -cpr=$custom_prior -ds=$dataset -dst=$data_max_time -dto=$data_time_offset
    done
    cd ../Libraries/QML_lib
    
    if [ $num_tests > 1 ]
    then
        python3 AnalyseMultipleQMD.py -dir=$long_dir --bayes_csv=$bayes_csv
    fi

fi 


# TODO google array job for PBS -- node exclusive flag
