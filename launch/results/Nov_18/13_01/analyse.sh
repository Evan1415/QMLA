
cd /home/bf16951/QMD/Launch/Results/Nov_18/13_01/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Nov_18/13_01/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Nov_18/13_01//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Nov_18/13_01//qmla.log     -top=5     -qhl=0     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Nov_18/13_01//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Nov_18/13_01//system_measurements.p     -ggr=DemoIsing     -plotprobes=/home/bf16951/QMD/Launch/Results/Nov_18/13_01//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Nov_18/13_01//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Nov_18/13_01/     -p=30     -e=5     -log=/home/bf16951/QMD/Launch/Results/Nov_18/13_01//qmla.log     -ggr=DemoIsing     -run_desc="localdevelopemt"     -git_commit=03d6a377f821e7c1183b85d0e8030230a76f669c     -qhl=0     -mqhl=1     -cb=/home/bf16951/QMD/Launch/Results/Nov_18/13_01//all_models_bayes_factors.csv 

