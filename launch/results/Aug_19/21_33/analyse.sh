
cd /home/bf16951/QMD/Launch/Results/Aug_19/21_33/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Aug_19/21_33/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Aug_19/21_33//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Aug_19/21_33//qmla.log     -top=5     -qhl=0     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Aug_19/21_33//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Aug_19/21_33//system_measurements.p     -ggr=FermiHubbardLatticeSet     -plotprobes=/home/bf16951/QMD/Launch/Results/Aug_19/21_33//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Aug_19/21_33//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=5     -dir=/home/bf16951/QMD/Launch/Results/Aug_19/21_33/     -p=10     -e=2     -log=/home/bf16951/QMD/Launch/Results/Aug_19/21_33//qmla.log     -ggr=FermiHubbardLatticeSet     -run_desc="localdevelopemt"     -git_commit=a3fc337f96dfef77b801471142b44a1c5c6528c1     -qhl=0     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Aug_19/21_33//all_models_bayes_factors.csv 

