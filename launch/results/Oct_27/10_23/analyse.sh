
cd /home/bf16951/QMD/Launch/Results/Oct_27/10_23/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Oct_27/10_23/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Oct_27/10_23//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Oct_27/10_23//qmla.log     -top=5     -qhl=1     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Oct_27/10_23//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Oct_27/10_23//system_measurements.p     -ggr=AnalyticalLikelihood     -plotprobes=/home/bf16951/QMD/Launch/Results/Oct_27/10_23//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Oct_27/10_23//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Oct_27/10_23/     -p=20000     -e=1000     -log=/home/bf16951/QMD/Launch/Results/Oct_27/10_23//qmla.log     -ggr=AnalyticalLikelihood     -run_desc="localdevelopemt"     -git_commit=64037f7c53d241918d5d5b86556ac64a7e63fa14     -qhl=1     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Oct_27/10_23//all_models_bayes_factors.csv 

