
cd /home/bf16951/QMD/Launch/Results/Aug_28/18_05/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Aug_28/18_05/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Aug_28/18_05//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Aug_28/18_05//qmla.log     -top=5     -qhl=1     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Aug_28/18_05//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Aug_28/18_05//system_measurements.p     -ggr=NVCentreGenticAlgorithmPrelearnedParameters     -plotprobes=/home/bf16951/QMD/Launch/Results/Aug_28/18_05//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Aug_28/18_05//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Aug_28/18_05/     -p=10     -e=2     -log=/home/bf16951/QMD/Launch/Results/Aug_28/18_05//qmla.log     -ggr=NVCentreGenticAlgorithmPrelearnedParameters     -run_desc="localdevelopemt"     -git_commit=7fac9ac3aef8cac103844acd3ee2ec97439971a5     -qhl=1     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Aug_28/18_05//all_models_bayes_factors.csv 

