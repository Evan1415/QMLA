
cd /home/bf16951/QMD/Launch/Results/Jul_28/15_11/
python3 ../../../../scripts/analyse_qmla.py     -dir=/home/bf16951/QMD/Launch/Results/Jul_28/15_11/     --bayes_csv=/home/bf16951/QMD/Launch/Results/Jul_28/15_11//bayes_factors.csv     -log=/home/bf16951/QMD/Launch/Results/Jul_28/15_11//qmla.log     -top=5     -qhl=1     -fqhl=0     -runinfo=/home/bf16951/QMD/Launch/Results/Jul_28/15_11//run_info.p     -sysmeas=/home/bf16951/QMD/Launch/Results/Jul_28/15_11//system_measurements.p     -ggr=NVCentreGenticAlgorithmPrelearnedParameters     -plotprobes=/home/bf16951/QMD/Launch/Results/Jul_28/15_11//plot_probes.p     -latex=/home/bf16951/QMD/Launch/Results/Jul_28/15_11//latex_mapping.txt     -gs=1

python3 ../../../../scripts/generate_results_pdf.py     -t=1     -dir=/home/bf16951/QMD/Launch/Results/Jul_28/15_11/     -p=2     -e=2     -log=/home/bf16951/QMD/Launch/Results/Jul_28/15_11//qmla.log     -ggr=NVCentreGenticAlgorithmPrelearnedParameters     -run_desc="localdevelopemt"     -git_commit=855c50371545a782a111adc060c0f6f158d0821d     -qhl=1     -mqhl=0     -cb=/home/bf16951/QMD/Launch/Results/Jul_28/15_11//bayes_factors.csv 

