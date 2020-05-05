#!/bin/bash
# note monitor script currently turned off (at very bottom)
# test_description="genetic-algorithm__longer-run"
# test_description='inspect-node-times__qhl__reset-zero-wt-policy'
# test_description="theory-test__ising-predetermined__2-models__4-site-true__champ-reduction__mixed-heuristic__medium-run"
# test_description='heis-predetermined__w-champ-reduction'
# test_description='fh-qhl'
# test_description='not_using_rq'
# test_description="testing-bf-reqmt-reduced-particles"
# test_description='ising_chain_shared_field'
# test_description='pauli-likewise-pairs-test__heis-xyz'
# test_description='fixed-lattice__test__heis-6-sites-qhl__2-proc'
# test_description='fixed-lattice__fermi-hubbard-qmla'
# test_description='qhl-TIME-TEST'
test_description='nv_simulation_3-sites-6-terms__QHL'
# test_description="genetic-algorithm__ising-model"

### ---------------------------------------------------###
# Essential choices for how to run multiple 
# instances of QMD from this script. 
### ---------------------------------------------------###

## Type/number of QMD(s) to run.
num_tests=20
num_processes_to_request=6
qhl=1 # do a test on QHL only -> 1; for full QMD -> 0
min_id=0 # update so instances don't clash and hit eachother's redis databases
multiple_qhl=0
multiple_growth_rules=0
do_further_qhl=0 # perform further QHL parameter tuning on average values found by QMD. 
experimental_data=0 # use experimental data -> 1; use fake data ->0
simulate_experiment=0

# QHL parameters.
e=500 # experiments
p=3000 # particles
ra=0.98 #resample a 
rt=0.5 # resample threshold
rp=1.0 # PGH factor
pgh_exp=1.0 # exponent to use in  time particle guess heuristic (PGH)
pgh_increase=0 # whether or not to increase the times found by PGH

### ---------------------------------------------------###
# Choose growth rule 
# will be determined by sim_growth_rule, exp_growth_rule, 
# and value of experimental_data.
### ---------------------------------------------------###

growth_rule='SimulatedNVCentre'
# growth_rule='FermiHubbardLatticeSet'
# growth_rule='IsingLatticeSet'
# growth_rule='HeisenbergLatticeSet'
# growth_rule='IsingSharedField'
# growth_rule='Genetic'
# growth_rule='IsingGenetic'

# Simulation growth rule
# sim_growth_rule='IsingProbabilistic'
# sim_growth_rule='IsingPredetermined'
# sim_growth_rule='IsingSharedField'
# sim_growth_rule='HeisenbergSharedField'
# sim_growth_rule='HeisenbergXYZPredetermined'
# sim_growth_rule='HeisenbergXYZProbabilistic'
# sim_growth_rule='FermiHubbardPredetermined'
# sim_growth_rule='FermiHubbardProbabilistic'
# sim_growth_rule='Genetic'
# sim_growth_rule='GeneticTest'
# sim_growth_rule='TestReducedParticlesBayesFactors'
# sim_growth_rule='TestAllParticlesBayesFactors'
# sim_growth_rule='NVExperimentalData'

### Experimental growth rules 
### which will overwrite growth_rule if exp_data==1

exp_growth_rule='ExperimentNVCentre'
# exp_growth_rule='ExperimentNVCentreNoTransvereTerms'
# exp_growth_rule='ExpAlternativeNV'
# exp_growth_rule='ExperimentFullAccessNV'
# exp_growth_rule='NVLargeSpinBath'
# exp_growth_rule='ExperimentNVCentreVaryTrueModel'
# exp_growth_rule='ExpNVRevivals'
# exp_growth_rule='ExperimentReducedNV'

# Choose a growth rule
#if (( "$experimental_data" == 1)) || (( "$simulate_experiment" == 1))
#then
#	growth_rule=$exp_growth_rule
#else
#	growth_rule=$sim_growth_rule
#fi

# Alternative growth rules, i.e. to learn alongside the true one. Used if multiple_growth_rules set to 1 above
alt_growth_rules=(  
#	'IsingPredetermined' 
#	'HeisenbergXYZPredetermined'
	'FermiHubbardPredetermined'
)
growth_rules_command=""
for item in ${alt_growth_rules[*]}
do
    growth_rules_command+=" -agr $item" 
done


### ---------------------------------------------------###
# The below parameters are used by QMD. 
# These should be considered by the user to ensure they match requirements. 
### ---------------------------------------------------###

# QMD settings - for learning (QHL) and comparison (BF)
bin_times_bayes_factors_default=1 # binning here means linspacing the times of both models for BF calc
num_probes=40
probe_noise_level_default=0.001
#probe_noise_level_default=0.0000001
use_all_times_bf_default=0
data_max_time=5 # to show in plots
top_number_models=3 # how many models to perform further QHL for
further_qhl_resource_factor=1
do_plots=0
pickle_class=0
custom_prior=1
gaussian=1 # set to 0 for uniform distribution, 1 for normal
param_min=0
param_max=10
param_mean=0.5
param_sigma=2
random_true_params=0 # if not random, then as set in qmla/SetQHLParams.py
random_prior=0 # if not random, then as set in qmla/SetQHLParams.py
resource_reallocation=0 # whether to weight num particles given to model based on number parameters it has
updater_from_prior=0 # 1->incorrect method of getting initial prior; 0->correct method copying entire updater
store_particles_weights=0



### ---------------------------------------------------###
# Everything from here downwards uses the parameters
# defined above to run QMD. 
# These do not need to be considered for every instance of QMD provided the default outputs are okay.
### ---------------------------------------------------###

### Create output files/directories
let max_id="$min_id + $num_tests - 1 "
this_dir=$(hostname)
day_time=$(date +%b_%d/%H_%M)
running_dir="$(pwd)"
#qmd_dir="${running_dir%/ParallelDevelopment}" # chop off ParallelDevelopment to get qmd folder path
qmd_dir="${running_dir%/Launch}" # chop off ParallelDevelopment to get qmd folder path
#lib_dir="$qmd_dir/Libraries/QML_lib"
lib_dir="$qmd_dir/qmla"
script_dir="$qmd_dir/Scripts"
results_dir=$day_time
full_path_to_results=$(pwd)/Results/$results_dir
all_qmd_bayes_csv="$full_path_to_results/cumulative.csv"
true_expec_filename="true_expec_vals.p"
true_expec_path="$full_path_to_results/$true_expec_filename"
latex_map_name='LatexMapping.txt'
latex_mapping_file=$full_path_to_results/$latex_map_name
OUT_LOG="$full_path_to_results/output_and_error_logs/"
output_file="output_file"
error_file="error_file" 
mkdir -p $full_path_to_results
mkdir -p $OUT_LOG
mkdir -p results_dir
copied_launch_file="$full_path_to_results/launched_script.txt"
cp $(pwd)/parallel_launch.sh $copied_launch_file
time=$test_time
qmd_id=$min_id
cutoff_time=600 # minimum time to request
max_seconds_reqd=0
global_server=$(hostname)
test_time="walltime=00:90:00"
echo "" > $full_path_to_results/job_ids_started.txt
echo "" > $full_path_to_results/job_ids_completed.txt
time_required_script="$full_path_to_results/set_time_env_vars.sh"
touch $time_required_script
chmod a+x $time_required_script
qmd_env_var="QMD_TIME"
qhl_env_var="QHL_TIME"
num_jobs_launched=0
prior_pickle_file="$full_path_to_results/prior.p"
true_params_pickle_file="$full_path_to_results/true_params.p"
plot_probe_file="$full_path_to_results/plot_probes.p"
results_path="$full_path_to_results/"
multi_qmd_log="$full_path_to_results/qmd_log.log"
git_commit="$(git rev-parse HEAD)"

### ---------------------------------------------------###
# Lists of QMD/QHL/BF params to loop over, e.g for parameter sweep
# Default is to only include parameters as defined above. 
### ---------------------------------------------------###
declare -a resample_a_values=(
$ra
#0.8
#0.9
#0.98
)

declare -a resample_thresh_values=(
$rt
#0.4
#0.5
#0.6
)

declare -a pgh_values=(
$rp
)

declare -a particle_counts=(
$p
)

declare -a experiment_counts=(
$e
)

declare -a probe_noise_options=(
$probe_noise_level_default
)


declare -a bin_time_options=(
$bin_times_bayes_factors_default
)

declare -a use_all_times_options=(
$use_all_times_bf_default
)



printf "$day_time: \t $test_description \t e=$e; p=$p; bt=$bt; ra=$ra; rt=$rt; rp=$rp; noise=$probe_noise_level_default; bintimesBF=$bin_times_bayes_factors \n" >> QMD_Results_directories.log
force_plot_plus=0
special_probe='random' #'ideal'
special_probe_plot='random'
time_request_insurance_factor=1
if (( "$bin_times_bayes_factors" == 1))
then
	let time_request_insurance_factor="2*$time_request_insurance_factor"
fi

if (( "$experimental_data" == 1))  
then
	force_plot_plus=1
#	special_probe='plus_random'
	special_probe='dec_13_exp'
#	special_probe='random'
#	special_probe='plus'
	special_probe_plot='plus' # test simulation using plus probe only.
	multiple_growth_rules=0
#	random_true_params=0
elif (( "$simulate_experiment" == 1))
then
	force_plot_plus=1
	multiple_growth_rules=0
#	special_probe='dec_13_exp'
	special_probe_plot='plus' # test simulation using plus probe only.
#	special_probe='random'
fi

### First set up parameters/data to be used by all instances of QMD for this run. 
# python3 ../qmla/SetQHLParams.py \
python3 ../Scripts/set_qmla_params.py \
	-true=$true_params_pickle_file \
	-prior=$prior_pickle_file \
	-probe=$plot_probe_file \
	-plus=$force_plot_plus \
	-pnoise=$probe_noise_level_default \
	-true_expec_path=$true_expec_path \
	-sp=$special_probe_plot \
	-dir=$results_path \
	-log=$multi_qmd_log \
	-g=$gaussian \
	-min=$param_min \
	-max=$param_max \
	-mean=$param_mean \
	-sigma=$param_sigma \
	-exp=$experimental_data \
	-ggr=$growth_rule \
	-rand_t=$random_true_params \
	-rand_p=$random_prior \
	$growth_rules_command


### Call script to determine how much time is needed based on above params. Store in QMD_TIME, QHL_TIME, etc. 
let temp_bayes_times="2*$e" # TODO fix time calculator
python3 ../Scripts/time_required_calculation.py \
	-ggr=$growth_rule \
	-use_agr=$multiple_growth_rules \
	$growth_rules_command \
	-e=$e \
	-p=$p \
	-bt=$temp_bayes_times \
	-proc=1 \
	-res=$resource_reallocation \
	-scr=$time_required_script \
	-time_insurance=$time_request_insurance_factor \
	-qmdtenv="QMD_TIME" \
	-qhltenv="QHL_TIME" \
	-fqhltenv="FQHL_TIME" \
	-num_proc_env="NUM_PROCESSES" \
	-mintime=1300
source $time_required_script
qmd_time=$QMD_TIME
qhl_time=$QHL_TIME
fqhl_time=$FQHL_TIME
num_processes=$NUM_PROCESSES # TODO RESTORE!!!!!!! testing without RQ
#num_processes=1
# Change requested time. e.g. if running QHL , don't need as many nodes. 
if (( "$qhl" == 1 )) || [[ "$experimental_growth_rule" == 'PT_Effective_Hamiltonian' ]]
then	
	num_proc=2
elif (( "multiple_qhl"  == 1 ))
then 
	num_proc=4
else
	num_proc=$num_processes
fi



node_req="nodes=1:ppn=$num_proc"


### ---------------------------------------------------###
# Call launch script within loop of parameters. 
### ---------------------------------------------------###
for bin_times_bayes_factors in "${bin_time_options[@]}";
do
	for use_all_times_bf in "${use_all_times_options[@]}";
	do

		for probe_noise_level in "${probe_noise_options[@]}";
		do
			for rp in "${pgh_values[@]}";
			do
				for rt in "${resample_thresh_values[@]}";
				do
					for ra in "${resample_a_values[@]}";
					do

						for p in  "${particle_counts[@]}";
						do
							for e in "${experiment_counts[@]}";
							do
								for i in `seq $min_id $max_id`;
								do
									let bt="$e"
									let qmd_id="$qmd_id+1"

									if [ "$qhl" == 1 ] || [ "$multiple_qhl" == 1 ] 
									then
										let seconds_reqd="$qhl_time"
									else
										let seconds_reqd="$qmd_time"
									fi

									let num_jobs_launched="$num_jobs_launched+1"
									time="walltime=00:00:$seconds_reqd"
									this_qmd_name="$test_description""_$qmd_id"
									this_error_file="$OUT_LOG/$error_file""_$qmd_id.txt"
									this_output_file="$OUT_LOG/$output_file""_$qmd_id.txt"
									printf "$day_time: \t e=$e; p=$p; bt=$bt; ra=$ra; rt=$rt; rp=$rp; qid=$qmd_id; seconds=$seconds_reqd; noise=$probe_noise_level; bintimesBF=$bin_times_bayes_factors \n" >> QMD_all_tasks.log

									qsub -v RUNNING_DIR=$running_dir,LIBRARY_DIR=$lib_dir,SCRIPT_DIR=$script_dir,ROOT_DIR=$qmd_dir,QMD_ID=$qmd_id,QHL=$qhl,MULTIPLE_QHL=$multiple_qhl,FURTHER_QHL=0,EXP_DATA=$experimental_data,GLOBAL_SERVER=$global_server,RESULTS_DIR=$full_path_to_results,DATETIME=$day_time,NUM_PARTICLES=$p,NUM_EXP=$e,NUM_BAYES=$bt,RESAMPLE_A=$ra,RESAMPLE_T=$rt,RESAMPLE_PGH=$rp,PGH_EXPONENT=$pgh_exp,PGH_INCREASE=$pgh_increase,PLOTS=$do_plots,PICKLE_QMD=$pickle_class,BAYES_CSV=$all_qmd_bayes_csv,CUSTOM_PRIOR=$custom_prior,STORE_PARTICLES_WEIGHTS=$store_particles_weights,DATA_MAX_TIME=$data_max_time,GROWTH=$growth_rule,MULTIPLE_GROWTH_RULES=$multiple_growth_rules,ALT_GROWTH="$growth_rules_command",LATEX_MAP_FILE=$latex_mapping_file,TRUE_PARAMS_FILE=$true_params_pickle_file,PRIOR_FILE=$prior_pickle_file,TRUE_EXPEC_PATH=$true_expec_path,PLOT_PROBES=$plot_probe_file,NUM_PROBES=$num_probes,SPECIAL_PROBE=$special_probe,PROBE_NOISE=$probe_noise_level,RESOURCE_REALLOCATION=$resource_reallocation,UPDATER_FROM_PRIOR=$updater_from_prior,GAUSSIAN=$gaussian,PARAM_MIN=$param_min,PARAM_MAX=$param_max,PARAM_MEAN=$param_mean,PARAM_SIGMA=$param_sigma,BIN_TIMES_BAYES=$bin_times_bayes_factors,BF_ALL_TIMES=$use_all_times_bf -N $this_qmd_name -l $node_req,$time -o $this_output_file -e $this_error_file run_qmd_instance.sh

								done
							done
						done
					done
				done
			done
		done
	done
done

finalise_qmd_script=$full_path_to_results/FINALISE_$test_description.sh
monitor_script=$full_path_to_results/monitor.sh
finalise_further_qhl_stage_script=$full_path_to_results/FURTHER_finalise.sh

### Generate script to analyse results of QMD runs. 
echo "
#!/bin/bash 
cd $script_dir
python3 analyse_qmla.py \
	-dir="$full_path_to_results" \
	-log=$multi_qmd_log \
	--bayes_csv=$all_qmd_bayes_csv \
	-top=$top_number_models \
	-qhl=$qhl \
	-fqhl=0 \
	-plot_probes=$plot_probe_file \
	-exp=$experimental_data \
	-params=$true_params_pickle_file \
	-true_expec=$true_expec_path \
	-latex=$latex_mapping_file \
	-gs=1 \
	-ggr=$growth_rule

python3 generate_results_pdf.py \
    -dir=$full_path_to_results \
    -p=$p -e=$e -bt=$bt -t=$num_tests \
    -nprobes=$num_probes \
    -pnoise=$probe_noise_level \
    -special_probe=$special_probe \
    -ggr=$growth_rule \
    -run_desc=$test_description \
    -git_commit=$git_commit \
    -ra=$ra \
    -rt=$rt \
    -pgh=$rp \
    -qhl=$qhl \
    -mqhl=$multiple_qhl \
    -cb=$all_qmd_bayes_csv \
    -exp=$experimental_data
" > $finalise_qmd_script

### Further QHL on best performing models. Add section to analysis script, which launches futher_qhl stage.


let p="$further_qhl_resource_factor*$p"
let e="$further_qhl_resource_factor*$e"
let bt="$e-1"
pgh=1.0 # further QHL on different times than initially trained on. 
#	rp=2.0
pbs_config=walltime=00:00:$fqhl_time,nodes=1:ppn=$top_number_models

echo "
do_further_qhl=$do_further_qhl
qmd_id=$qmd_id
cd $(pwd)
if (( "\$do_further_qhl" == 1 ))
then

	for i in \`seq $min_id $max_id\`;
	do
		let qmd_id="1+\$qmd_id"
		finalise_script="finalise_$test_description_\$qmd_id"
		qsub -v QMD_ID=\$qmd_id,QHL=0,FURTHER_QHL=1,EXP_DATA=$experimental_data,RUNNING_DIR=$running_dir,LIBRARY_DIR=$lib_dir,SCRIPT_DIR=$script_dir,GLOBAL_SERVER=$global_server,RESULTS_DIR=$full_path_to_results,DATETIME=$day_time,NUM_PARTICLES=$p,NUM_EXP=$e,NUM_BAYES=$bt,RESAMPLE_A=$ra,RESAMPLE_T=$rt,RESAMPLE_PGH=$rp,PLOTS=$do_plots,PICKLE_QMD=$pickle_class,BAYES_CSV=$all_qmd_bayes_csv,CUSTOM_PRIOR=$custom_prior,DATA_MAX_TIME=$data_max_time,GROWTH=$growth_rule,LATEX_MAP_FILE=$latex_mapping_file,TRUE_PARAMS_FILE=$true_params_pickle_file,PRIOR_FILE=$prior_pickle_file,TRUE_EXPEC_PATH=$true_expec_path,PLOT_PROBES=$plot_probe_file,RESOURCE_REALLOCATION=$resource_reallocation,UPDATER_FROM_PRIOR=$updater_from_prior,GAUSSIAN=$gaussian,PARAM_MIN=$param_min,PARAM_MAX=$param_max,PARAM_MEAN=$param_mean,PARAM_SIGMA=$param_sigma -N \$finalise_script -l $pbs_config -o $OUT_LOG/finalise_output.txt -e $OUT_LOG/finalise_error.txt run_qmd_instance.sh 
	done 
fi
" >> $finalise_qmd_script

echo "
	#!/bin/bash 
	cd $script_dir
	python3 analyse_qmla.py \
		-dir="$full_path_to_results" \
		-log=$multi_qmd_log \
		--bayes_csv=$all_qmd_bayes_csv \
		-top=$top_number_models 
		-qhl=$qhl \
		-fqhl=1 \
		-exp=$experimental_data \
		-latex==$latex_mapping_file \
		-params=$true_params_pickle_file \
		-true_expec=$true_expec_path \
		-ggr=$growth_rule \
		-plot_probes=$plot_probe_file

	python3 generate_results_pdf.py \
		-dir=$full_path_to_results \
		-p=$p -e=$e -bt=$bt -t=$num_tests \
		-nprobes=$num_probes \
		-pnoise=$probe_noise_level \
		-special_probe=$special_probe \
		-ggr=$growth_rule \
		-run_desc=$test_description \
		-git_commit=$git_commit \
		-ra=$ra \
		-rt=$rt \
		-pgh=$rp \
		-qhl=$qhl \
		-mqhl=$multiple_qhl \
		-cb=$all_qmd_bayes_csv \
		-exp=$experimental_data \
		-out="further_qhl_analysis"
" > $finalise_further_qhl_stage_script
chmod a+x $finalise_further_qhl_stage_script



### Generate script to monitor instances of QMD and launch futher analysis when all instances have finished.
echo " 

#!/bin/bash

echo \"inside monitor script.\"
IFS=$'\n' read -d '' -r -a job_ids_s < $full_path_to_results/job_ids_started.txt
num_jobs_started=\${#job_ids_s[@]}

IFS=$'\n' read -d '' -r -a job_ids_c < $full_path_to_results/job_ids_completed.txt
num_jobs_complete=\${#job_ids_c[@]}

for k in \${job_ids_c[@]}
do
	echo \$k
done


echo \"num jobs started/finished: \$num_jobs_started \$num_jobs_complete\"

while (( \$num_jobs_complete < $num_jobs_launched ))
do
	IFS=$'\n' read -d '' -r -a job_ids_s < $full_path_to_results/job_ids_started.txt
	num_jobs_started=\${#job_ids_s[@]}

	IFS=$'\n' read -d '' -r -a job_ids_c < $full_path_to_results/job_ids_completed.txt
	num_jobs_complete=\${#job_ids_c[@]}

	echo \"Waiting. Currently \$num_jobs_complete / \$num_jobs_started \"
	sleep 3
done

sh $finalise_qmd_script
" > $monitor_script

let max_seconds_reqd="$seconds_reqd + 15"
chmod a+x $monitor_script
chmod a+x $finalise_qmd_script
#qsub -l walltime=00:00:$max_seconds_reqd,nodes=1:ppn=1 -N monitor_$test_description -o $OUT_LOG/monitor_output.txt -e $OUT_LOG/monitor_error.txt $monitor_script
