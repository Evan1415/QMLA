
cd /home/bf16951/QMD/Launch/Results/Nov_18/13_56/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Nov_18/13_56/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Nov_18/13_56//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Nov_18/13_56//qmla.log     -top=5     -qhl=0     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Nov_18/13_56//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Nov_18/13_56//system_measurements.p     -ggr=DemoIsing     -plotprobes=/home/bf16951/QMD/Launch/Results/Nov_18/13_56//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Nov_18/13_56//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Nov_18/13_56/     -p=5000     -e=1000     -log=/home/bf16951/QMD/Launch/Results/Nov_18/13_56//qmla.log     -ggr=DemoIsing     -run_desc="localdevelopemt"     -git_commit=3f3e858b2723ac11034f5f92824aecf20d98bd88     -qhl=0     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Nov_18/13_56//all_models_bayes_factors.csv 

