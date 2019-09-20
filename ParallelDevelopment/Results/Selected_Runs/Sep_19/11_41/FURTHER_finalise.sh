
	#!/bin/bash 
	cd /panfs/panasas01/phys/bf16951/QMD/Libraries/QML_lib
	python3 AnalyseMultipleQMD.py 		-dir=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_19/11_41 		--bayes_csv=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_19/11_41/cumulative.csv 		-top=3 
		-qhl=0 		-fqhl=1 		-exp=0 		-latex==/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_19/11_41/LatexMapping.txt 		-params=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_19/11_41/true_params.p 		-true_expec=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_19/11_41/true_expec_vals.p 		-ggr=two_qubit_ising_rotation_hyperfine_transverse 		-plot_probes=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_19/11_41/plot_probes.p

	python3 CombineAnalysisPlots.py 		-dir=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_19/11_41 		-p=2500 -e=750 -bt=749 -t=50 		-nprobes=40 		-pnoise=0.001 		-special_probe=random 		-ggr=two_qubit_ising_rotation_hyperfine_transverse 		-run_desc=NV-exp-method-sim__probe-with-phase__same-probe__reduced-true-mod 		-git_commit=8245f7a6b7c89967b528103210f9acd34f1d818e 		-ra=0.98 		-rt=0.5 		-pgh=1.0 		-qhl=0 		-mqhl=0 		-cb=/panfs/panasas01/phys/bf16951/QMD/ParallelDevelopment/Results/Sep_19/11_41/cumulative.csv 		-exp=0 		-out=further_qhl_analysis

