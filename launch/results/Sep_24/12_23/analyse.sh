
cd /home/bf16951/QMD/Launch/Results/Sep_24/12_23/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Sep_24/12_23/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Sep_24/12_23//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Sep_24/12_23//qmla.log     -top=5     -qhl=1     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Sep_24/12_23//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Sep_24/12_23//system_measurements.p     -ggr=HeisenbergGeneticXXZ     -plotprobes=/home/bf16951/QMD/Launch/Results/Sep_24/12_23//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Sep_24/12_23//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Sep_24/12_23/     -p=3000     -e=1000     -log=/home/bf16951/QMD/Launch/Results/Sep_24/12_23//qmla.log     -ggr=HeisenbergGeneticXXZ     -run_desc="localdevelopemt"     -git_commit=015ce1ba2b0646d510be3208ba51e5a873615d9a     -qhl=1     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Sep_24/12_23//all_models_bayes_factors.csv 

