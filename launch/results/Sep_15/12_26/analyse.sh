
cd /home/bf16951/QMD/Launch/Results/Sep_15/12_26/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Sep_15/12_26/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Sep_15/12_26//all_models_bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Sep_15/12_26//qmla.log     -top=5     -qhl=0     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Sep_15/12_26//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Sep_15/12_26//system_measurements.p     -ggr=ObjFncRank     -plotprobes=/home/bf16951/QMD/Launch/Results/Sep_15/12_26//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Sep_15/12_26//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Sep_15/12_26/     -p=10     -e=2     -log=/home/bf16951/QMD/Launch/Results/Sep_15/12_26//qmla.log     -ggr=ObjFncRank     -run_desc="localdevelopemt"     -git_commit=55743fabb22480a47f477bf20480f7d3568d0040     -qhl=0     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Sep_15/12_26//all_models_bayes_factors.csv 

