#!/bin/bash

max_qmd_id=10
directory="multtestdir/"

cwd=$(pwd)
long_dir="$cwd/Results/$directory"
bcsv="cumulative.csv"
bayes_csv="$long_dir$bcsv"

this_log="$cwd/dev_exp.log"

rm -r $long_dir
rm $this_log
mkdir -p $long_dir
mkdir -p $directory

q_id=0
for i in `seq 1 2`;
do
    for j in `seq 1 1`;
    do
        let num_prt="$i+10"
        redis-cli flushall
        let q_id="$q_id+1"
        python3 Exp.py -p=20 -e=5 -rq=0 -g=1 -dir=$long_dir -qid=$q_id -pt=1 -pkl=1 -log=$this_log -cb=$bayes_csv 
    done 
done

cd ../Libraries/QML_lib
python3 AnalyseMultipleQMD.py -dir=$long_dir --bayes_csv=$bayes_csv


# TODO google array job for PBS -- node exclusive flag
