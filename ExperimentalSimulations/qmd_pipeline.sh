#!/bin/bash

test_description="qmd_runs"
num_tests=1
let max_qmd_id="$num_tests"

day_time=$(date +%b_%d/%H_%M)
directory="$day_time/"

cwd=$(pwd)
long_dir="$cwd/Results/$day_time/"
bcsv="cumulative.csv"
bayes_csv="$long_dir$bcsv"

this_log="$long_dir/qmd.log"
furhter_qhl_log="$long_dir/qhl_further.log"

# rm -r $long_dir
# rm $this_log
mkdir -p $long_dir
#mkdir -p $directory


true_operator='xTiPPyTiPPzTiPPxTxPPyTyPPzTz'
declare -a qhl_operators=(
    $true_operator
)
qhl_test=0
do_further_qhl=1
top_number_models=1
q_id=0
exp_data=1
#growth_rule='two_qubit_ising_rotation_hyperfine'
growth_rule='two_qubit_ising_rotation_hyperfine_transverse'
use_rq=0
prt=20
exp=8
further_qhl_factor=2
use_rq=0
if (($prt > 50)) || (($exp > 10)) || (( $qhl_test == 1 ))
then
    use_rq=1
else
    use_rq=0
fi
# use_rq=0
let bt="$exp-1"
pgh=0.3
ra=0.8
rt=0.5
gaussian=1
custom_prior=1
#dataset='NVB_HahnPeaks_Newdata'
dataset='NV05_HahnEcho02'
#dataset='NV05_HahnPeaks_expdataset'
data_max_time=5000 # nanoseconds
data_time_offset=205 # nanoseconds


printf "$day_time: \t $test_description \n" >> QMD_Results_directories.log
# Launch $num_tests instances of QMD 

declare -a particle_counts=(
$prt
)
for prt in  "${particle_counts[@]}";
do
    for i in `seq 1 $max_qmd_id`;
    do
        redis-cli flushall
        let q_id="$q_id+1"
        python3 Exp.py \
            -op=$true_operator -p=$prt -e=$exp -bt=$bt \
            -rq=$use_rq -g=$gaussian -qhl=$qhl_test \
            -ra=$ra -rt=$rt -pgh=$pgh \
            -dir=$long_dir -qid=$q_id -pt=1 -pkl=1 \
            -log=$this_log -cb=$bayes_csv \
            -exp=$exp_data -cpr=$custom_prior \
            -ds=$dataset -dst=$data_max_time -dto=$data_time_offset \
            -ggr=$growth_rule
    done
done

# Analyse results of QMD. (Only after QMD, not QHL).
python3 ../Libraries/QML_lib/AnalyseMultipleQMD.py \
    -dir=$long_dir --bayes_csv=$bayes_csv \
    -top=$top_number_models -qhl=$qhl_test


if (( $do_further_qhl == 1 )) 
then
    pgh=0.5 # train on different set of data
    redis-cli flushall 
    let particles="$further_qhl_factor * $prt"
    let experiments="$further_qhl_factor * $exp"
#    let q_id="$q_id+1"
    python3 Exp.py \
        -fq=$do_further_qhl \
        -p=$particles -e=$experiments -bt=$bt \
        -rq=$use_rq -g=$gaussian -qhl=0 \
        -ra=$ra -rt=$rt -pgh=$pgh \
        -dir=$long_dir -qid=$q_id -pt=1 -pkl=0 \
        -log=$this_log -cb=$bayes_csv \
        -exp=$exp_data -cpr=$custom_prior \
        -ds=$dataset -dst=$data_max_time -dto=$data_time_offset \
        -ggr=$growth_rule
fi

