
cd /home/bf16951/QMD/Launch/Results/Jul_29/17_10/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Jul_29/17_10/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Jul_29/17_10//bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Jul_29/17_10//qmla.log     -top=5     -qhl=1     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Jul_29/17_10//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Jul_29/17_10//system_measurements.p     -ggr=FermiHubbardLatticeSet     -plotprobes=/home/bf16951/QMD/Launch/Results/Jul_29/17_10//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Jul_29/17_10//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Jul_29/17_10/     -p=10     -e=2     -log=/home/bf16951/QMD/Launch/Results/Jul_29/17_10//qmla.log     -ggr=FermiHubbardLatticeSet     -run_desc="localdevelopemt"     -git_commit=1c33ba306817d0e154a9697cb65e222f78963638     -qhl=1     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Jul_29/17_10//bayes_factors.csv 

