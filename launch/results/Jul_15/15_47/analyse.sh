
cd /home/bf16951/QMD/Launch/Results/Jul_15/15_47/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Jul_15/15_47/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Jul_15/15_47//bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Jul_15/15_47//qmla.log     -top=5     -qhl=1     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Jul_15/15_47//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Jul_15/15_47//system_measurements.p     -ggr=NVCentreGenticAlgorithmPrelearnedParameters     -plotprobes=/home/bf16951/QMD/Launch/Results/Jul_15/15_47//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Jul_15/15_47//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Jul_15/15_47/     -p=10     -e=2     -log=/home/bf16951/QMD/Launch/Results/Jul_15/15_47//qmla.log     -ggr=NVCentreGenticAlgorithmPrelearnedParameters     -run_desc="localdevelopemt"     -git_commit=1d6e357e4c73832afbb597cf1da5d57ea6c7f7df     -qhl=1     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Jul_15/15_47//bayes_factors.csv 

