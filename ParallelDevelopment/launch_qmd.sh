#!/bin/bash

test_description="QMD_broad_prior_not_exp_data"

num_tests=1
min_id=0 # update so instances don't clash and hit eachother's redis databases
let max_id="$min_id + $num_tests - 1 "


this_dir=$(hostname)
day_time=$(date +%b_%d/%H_%M)

script_dir="/panfs/panasas01/phys/bf16951/QMD/ExperimentalSimulations"
lib_dir="/panfs/panasas01/phys/bf16951/QMD/Libraries/QML_lib"
results_dir=$day_time
# full_path_to_results=$script_dir/Results/$results_dir
full_path_to_results=$(pwd)/Results/$results_dir
all_qmd_bayes_csv="$full_path_to_results/multiQMD.csv"


OUT_LOG="$full_path_to_results/OUTPUT_AND_ERROR_FILES/"
echo "pwd: $(pwd)"
echo "OUT LOG: $OUT_LOG"
output_file="output_file"
error_file="error_file" 

mkdir -p $full_path_to_results
mkdir -p "$(pwd)/logs"
mkdir -p $OUT_LOG
mkdir -p results_dir

global_server=$(hostname)
test_time="walltime=00:90:00"

time=$test_time
qmd_id=$min_id
cutoff_time=180

## QMD parameters
do_plots=0
pickle_class=0
qhl=0
experimental_data=1

p=50
e=20
ra=0.95
rt=0.5
rp=0.3

true_hamiltonian='xTiPPyTiPPzTiPPxTxPPyTyPPzTz'

declare -a qhl_operators=(
'xTiPPyTiPPzTiPPxTxPPyTyPPzTz'
)

declare -a particle_counts=(
$p
)

declare -a experiment_counts=(
$e
)


printf "$day_time: \t $test_description \t e=$e; p=$p; bt=$bt; ra=$ra; rt=$rt; rp=$rp \n" >> QMD_Results_directories.log

if [ "$qhl" == 1 ]
then
    for op in "${qhl_operators[@]}";
	do
		for p in  "${particle_counts[@]}";
		do
			for e in "${experiment_counts[@]}";
			do
				for i in `seq $min_id $max_id`;
				do
					let bt="$e/2"
					let qmd_id="$qmd_id+1"
					let ham_exp="$e*$p + $p*$bt"
					let expected_time="$ham_exp/50"

					if [ "$qhl" == 1 ]
					then
						let expected_time="$expected_time/10"
					fi

					if (( $expected_time < $cutoff_time));
					then
						seconds_reqd=$cutoff_time	
					else
						seconds_reqd=$expected_time	
					fi
					time="walltime=00:00:$seconds_reqd"
					this_qmd_name="$test_description""_$qmd_id"
					this_error_file="$OUT_LOG/$error_file""_$qmd_id.txt"
					this_output_file="$OUT_LOG/$output_file""_$qmd_id.txt"
					printf "$day_time: \t e=$e; p=$p; bt=$bt; ra=$ra; rt=$rt; rp=$rp; qid=$qmd_id; seconds=$seconds_reqd \n" >> QMD_all_tasks.log

					qsub -v QMD_ID=$qmd_id,OP="$op",QHL=$qhl,EXP_DATA=$experimental_data,GLOBAL_SERVER=$global_server,RESULTS_DIR=$full_path_to_results,DATETIME=$day_time,NUM_PARTICLES=$p,NUM_EXP=$e,NUM_BAYES=$bt,RESAMPLE_A=$ra,RESAMPLE_T=$rt,RESAMPLE_PGH=$rp,PLOTS=$do_plots,PICKLE_QMD=$pickle_class,BAYES_CSV=$all_qmd_bayes_csv -N $this_qmd_name -l $time -o $this_output_file -e $this_error_file run_qmd_instance.sh

				done
			done
		done
	done

else 
	for p in  "${particle_counts[@]}";
	do
		for e in "${experiment_counts[@]}";
		do
			for i in `seq $min_id $max_id`;
			do
				let bt="$e/2"
				let qmd_id="$qmd_id+1"
				let ham_exp="$e*$p + $p*$bt"
				let expected_time="$ham_exp/50"
				if (( $expected_time < $cutoff_time));
				then
					seconds_reqd=$cutoff_time	
				else
					seconds_reqd=$expected_time	
				fi
				time="walltime=00:00:$seconds_reqd"
				this_qmd_name="$test_description""_$qmd_id"
				this_error_file="$OUT_LOG/$error_file""_$qmd_id.txt"
				this_output_file="$OUT_LOG/$output_file""_$qmd_id.txt"
				printf "$day_time: \t e=$e; p=$p; bt=$bt; ra=$ra; rt=$rt; rp=$rp; qid=$qmd_id; seconds=$seconds_reqd \n" >> QMD_all_tasks.log

				qsub -v QMD_ID=$qmd_id,OP="$true_hamiltonian",QHL=$qhl,EXP_DATA=$experimental_data,GLOBAL_SERVER=$global_server,RESULTS_DIR=$full_path_to_results,DATETIME=$day_time,NUM_PARTICLES=$p,NUM_EXP=$e,NUM_BAYES=$bt,RESAMPLE_A=$ra,RESAMPLE_T=$rt,RESAMPLE_PGH=$rp,PLOTS=$do_plots,PICKLE_QMD=$pickle_class,BAYES_CSV=$all_qmd_bayes_csv -N $this_qmd_name -l $time -o $this_output_file -e $this_error_file run_qmd_instance.sh

			done
		done
	done




fi

echo "
#!/bin/bash 
cd $lib_dir
python3 AnalyseMultipleQMD.py -dir="$full_path_to_results" --bayes_csv=$all_qmd_bayes_csv
" > $full_path_to_results/ANALYSE_$test_description.sh
