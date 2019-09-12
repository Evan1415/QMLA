
	#!/bin/bash 
	cd /panfs/panasas01/phys/bf16951/QMD/Libraries/QML_lib
	python3 AnalyseMultipleQMD.py 		-dir=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_12/11_56 		--bayes_csv=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_12/11_56/cumulative.csv 		-top=3 
		-qhl=0 		-fqhl=1 		-exp=0 		-latex==/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_12/11_56/LatexMapping.txt 		-params=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_12/11_56/true_params.p 		-true_expec=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_12/11_56/true_expec_vals.p 		-ggr=NV_alternative_model 		-plot_probes=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_12/11_56/plot_probes.p

	python3 CombineAnalysisPlots.py 		-dir=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_12/11_56 		-p=30 -e=10 -bt=9 -t=15 		-nprobes=40 		-pnoise=0.001 		-special_probe=random 		-ggr=NV_alternative_model 		-run_desc=short-run-data-for-generating-plots__simulation-rand-probe 		-git_commit=57dc67745b04ad1b0e8a20642e4302b5f1ab7aaa 		-ra=0.98 		-rt=0.5 		-pgh=1.0 		-qhl=0 		-mqhl=0 		-cb=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_12/11_56/cumulative.csv 		-exp=0 		-out=further_qhl_analysis

