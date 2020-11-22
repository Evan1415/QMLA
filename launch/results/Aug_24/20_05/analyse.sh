
cd /home/bf16951/QMD/Launch/Results/Aug_24/20_05/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Aug_24/20_05/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Aug_24/20_05//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Aug_24/20_05//qmla.log     -top=5     -qhl=0     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Aug_24/20_05//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Aug_24/20_05//system_measurements.p     -ggr=IsingGeneticTest     -plotprobes=/home/bf16951/QMD/Launch/Results/Aug_24/20_05//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Aug_24/20_05//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Aug_24/20_05/     -p=10     -e=2     -log=/home/bf16951/QMD/Launch/Results/Aug_24/20_05//qmla.log     -ggr=IsingGeneticTest     -run_desc="localdevelopemt"     -git_commit=2ae0078c4263666ebc55df72f5065f18a789600d     -qhl=0     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Aug_24/20_05//all_models_bayes_factors.csv 

