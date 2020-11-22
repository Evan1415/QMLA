
cd /home/bf16951/QMD/Launch/Results/Sep_24/14_51/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Sep_24/14_51/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Sep_24/14_51//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Sep_24/14_51//qmla.log     -top=5     -qhl=1     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Sep_24/14_51//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Sep_24/14_51//system_measurements.p     -ggr=HeisenbergGeneticXXZ     -plotprobes=/home/bf16951/QMD/Launch/Results/Sep_24/14_51//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Sep_24/14_51//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Sep_24/14_51/     -p=30     -e=10     -log=/home/bf16951/QMD/Launch/Results/Sep_24/14_51//qmla.log     -ggr=HeisenbergGeneticXXZ     -run_desc="localdevelopemt"     -git_commit=e9aae3b7574076fc2233ae21fa756b318d4736c9     -qhl=1     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Sep_24/14_51//all_models_bayes_factors.csv 

