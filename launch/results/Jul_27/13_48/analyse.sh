
cd /home/bf16951/QMD/Launch/Results/Jul_27/13_48/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Jul_27/13_48/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Jul_27/13_48//bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Jul_27/13_48//qmla.log     -top=5     -qhl=0     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Jul_27/13_48//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Jul_27/13_48//system_measurements.p     -ggr=NVCentreGenticAlgorithmPrelearnedParameters     -plotprobes=/home/bf16951/QMD/Launch/Results/Jul_27/13_48//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Jul_27/13_48//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Jul_27/13_48/     -p=2     -e=2     -log=/home/bf16951/QMD/Launch/Results/Jul_27/13_48//qmla.log     -ggr=NVCentreGenticAlgorithmPrelearnedParameters     -run_desc="localdevelopemt"     -git_commit=3545c87ab467bae3c8a644287d09c271f35c816c     -qhl=0     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Jul_27/13_48//bayes_factors.csv 

