
cd /home/bf16951/QMD/Launch/Results/Sep_07/23_03/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Sep_07/23_03/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Sep_07/23_03//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Sep_07/23_03//qmla.log     -top=5     -qhl=0     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Sep_07/23_03//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Sep_07/23_03//system_measurements.p     -ggr=NVCentreGenticAlgorithmPrelearnedParameters     -plotprobes=/home/bf16951/QMD/Launch/Results/Sep_07/23_03//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Sep_07/23_03//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Sep_07/23_03/     -p=10     -e=2     -log=/home/bf16951/QMD/Launch/Results/Sep_07/23_03//qmla.log     -ggr=NVCentreGenticAlgorithmPrelearnedParameters     -run_desc="localdevelopemt"     -git_commit=ffeec6e30b58d8e361a236e262abe045e2d5423f     -qhl=0     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Sep_07/23_03//all_models_bayes_factors.csv 

