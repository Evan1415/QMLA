
cd /home/bf16951/QMD/Launch/Results/Nov_14/17_00/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Nov_14/17_00/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Nov_14/17_00//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Nov_14/17_00//qmla.log     -top=5     -qhl=1     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Nov_14/17_00//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Nov_14/17_00//system_measurements.p     -ggr=ThesisLatticeDemo     -plotprobes=/home/bf16951/QMD/Launch/Results/Nov_14/17_00//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Nov_14/17_00//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Nov_14/17_00/     -p=100     -e=20     -log=/home/bf16951/QMD/Launch/Results/Nov_14/17_00//qmla.log     -ggr=ThesisLatticeDemo     -run_desc="localdevelopemt"     -git_commit=244f7ce0ab791f419a2dec9ab14bbcff9893899d     -qhl=1     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Nov_14/17_00//all_models_bayes_factors.csv 

