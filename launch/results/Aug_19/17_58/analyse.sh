
cd /home/bf16951/QMD/Launch/Results/Aug_19/17_58/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Aug_19/17_58/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Aug_19/17_58//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Aug_19/17_58//qmla.log     -top=5     -qhl=0     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Aug_19/17_58//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Aug_19/17_58//system_measurements.p     -ggr=FermiHubbardLatticeSet     -plotprobes=/home/bf16951/QMD/Launch/Results/Aug_19/17_58//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Aug_19/17_58//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Aug_19/17_58/     -p=10     -e=2     -log=/home/bf16951/QMD/Launch/Results/Aug_19/17_58//qmla.log     -ggr=FermiHubbardLatticeSet     -run_desc="localdevelopemt"     -git_commit=f757fb701a4ab191ccad629f3662a370f85f0e93     -qhl=0     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Aug_19/17_58//all_models_bayes_factors.csv 

