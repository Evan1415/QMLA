
cd /home/bf16951/QMD/Launch/Results/Aug_26/11_40/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Aug_26/11_40/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Aug_26/11_40//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Aug_26/11_40//qmla.log     -top=5     -qhl=0     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Aug_26/11_40//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Aug_26/11_40//system_measurements.p     -ggr=IsingGeneticSingleLayer     -plotprobes=/home/bf16951/QMD/Launch/Results/Aug_26/11_40//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Aug_26/11_40//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Aug_26/11_40/     -p=10     -e=2     -log=/home/bf16951/QMD/Launch/Results/Aug_26/11_40//qmla.log     -ggr=IsingGeneticSingleLayer     -run_desc="localdevelopemt"     -git_commit=6f3e8dce349eead9b057de19fdfcca6752b2ed68     -qhl=0     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Aug_26/11_40//all_models_bayes_factors.csv 

