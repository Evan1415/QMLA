
cd /home/bf16951/QMD/Launch/Results/Aug_17/22_03/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Aug_17/22_03/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Aug_17/22_03//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Aug_17/22_03//qmla.log     -top=5     -qhl=0     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Aug_17/22_03//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Aug_17/22_03//system_measurements.p     -ggr=HeisenbergGenetic     -plotprobes=/home/bf16951/QMD/Launch/Results/Aug_17/22_03//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Aug_17/22_03//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=0     -dir=/home/bf16951/QMD/Launch/Results/Aug_17/22_03/     -p=10     -e=2     -log=/home/bf16951/QMD/Launch/Results/Aug_17/22_03//qmla.log     -ggr=HeisenbergGenetic     -run_desc="localdevelopemt"     -git_commit=223780943ab69c437ab13018c6b7677b6c0f1169     -qhl=0     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Aug_17/22_03//all_models_bayes_factors.csv 

