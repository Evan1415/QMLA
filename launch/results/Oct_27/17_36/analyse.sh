
cd /home/bf16951/QMD/Launch/Results/Oct_27/17_36/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Oct_27/17_36/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Oct_27/17_36//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Oct_27/17_36//qmla.log     -top=5     -qhl=1     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Oct_27/17_36//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Oct_27/17_36//system_measurements.p     -ggr=     -plotprobes=/home/bf16951/QMD/Launch/Results/Oct_27/17_36//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Oct_27/17_36//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Oct_27/17_36/     -p=10     -e=10     -log=/home/bf16951/QMD/Launch/Results/Oct_27/17_36//qmla.log     -ggr=     -run_desc="localdevelopemt"     -git_commit=64037f7c53d241918d5d5b86556ac64a7e63fa14     -qhl=1     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Oct_27/17_36//all_models_bayes_factors.csv 

