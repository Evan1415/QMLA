
#!/bin/bash 
cd /home/bf16951/Dropbox/QML_share_stateofart/QMD/Libraries/QML_lib
python3 AnalyseMultipleQMD.py 	-dir=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00 	--bayes_csv=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/cumulative.csv 	-top=3 	-qhl=0 	-fqhl=0 	-plot_probes=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/plot_probes.p 	-exp=1 	-params=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/true_params.p 	-true_expec=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/true_expec_vals.p 	-latex=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/LatexMapping.txt 	-ggr=two_qubit_ising_rotation_hyperfine_transverse

python3 CombineAnalysisPlots.py     -dir=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00     -p=2500 -e=750 -bt=750 -t=115     -nprobes=40     -pnoise=0.001     -special_probe=dec_13_exp     -ggr=two_qubit_ising_rotation_hyperfine_transverse     -run_desc=simulate-nv-experiment__+R-probe     -git_commit=f727f88be9318ac743b9d3fd5e3f1b85f144a69f     -ra=0.98     -rt=0.5     -pgh=1.0     -qhl=0     -mqhl=0     -cb=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/cumulative.csv     -exp=1


do_further_qhl=0
qmd_id=116
cd /home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment
if (( $do_further_qhl == 1 ))
then

	for i in `seq 1 115`;
	do
		let qmd_id=1+$qmd_id
		finalise_script=finalise_$qmd_id
		qsub -v QMD_ID=$qmd_id,QHL=0,FURTHER_QHL=1,EXP_DATA=1,RUNNING_DIR=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment,LIBRARY_DIR=/home/bf16951/Dropbox/QML_share_stateofart/QMD/Libraries/QML_lib,SCRIPT_DIR=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ExperimentalSimulations,GLOBAL_SERVER=newblue1,RESULTS_DIR=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00,DATETIME=Aug_16/18_00,NUM_PARTICLES=2500,NUM_EXP=750,NUM_BAYES=749,RESAMPLE_A=0.98,RESAMPLE_T=0.5,RESAMPLE_PGH=1.0,PLOTS=0,PICKLE_QMD=0,BAYES_CSV=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/cumulative.csv,CUSTOM_PRIOR=1,DATA_MAX_TIME=15,GROWTH=two_qubit_ising_rotation_hyperfine_transverse,LATEX_MAP_FILE=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/LatexMapping.txt,TRUE_PARAMS_FILE=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/true_params.p,PRIOR_FILE=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/prior.p,TRUE_EXPEC_PATH=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/true_expec_vals.p,PLOT_PROBES=/home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/plot_probes.p,RESOURCE_REALLOCATION=0,UPDATER_FROM_PRIOR=0,GAUSSIAN=1,PARAM_MIN=0,PARAM_MAX=10,PARAM_MEAN=0.5,PARAM_SIGMA=2 -N $finalise_script -l walltime=00:00:19493,nodes=1:ppn=3 -o /home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/output_and_error_logs//finalise_output.txt -e /home/bf16951/Dropbox/QML_share_stateofart/QMD/ParallelDevelopment/Results/Selected_Runs/Aug_16/18_00/output_and_error_logs//finalise_error.txt run_qmd_instance.sh 
	done 
fi

