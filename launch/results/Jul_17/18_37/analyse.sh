
cd /home/bf16951/QMD/Launch/Results/Jul_17/18_37/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Jul_17/18_37/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Jul_17/18_37//bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Jul_17/18_37//qmla.log     -top=5     -qhl=0     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Jul_17/18_37//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Jul_17/18_37//system_measurements.p     -ggr=NVCentreGenticAlgorithmPrelearnedParameters     -plotprobes=/home/bf16951/QMD/Launch/Results/Jul_17/18_37//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Jul_17/18_37//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Jul_17/18_37/     -p=2     -e=2     -log=/home/bf16951/QMD/Launch/Results/Jul_17/18_37//qmla.log     -ggr=NVCentreGenticAlgorithmPrelearnedParameters     -run_desc="localdevelopemt"     -git_commit=80854389433f1272976932d401813c780ed07f60     -qhl=0     -mqhl=1     -cb=/home/bf16951/QMD/Launch/Results/Jul_17/18_37//bayes_factors.csv 

