import random
import pickle
import argparse
import UserFunctions
import DataBase

### SET VALUES HERE ###
# set_prior_specific_terms = {
# 	'xTi' : [3.0, 2.0], # TODO Broaden, testing with small dist
# 	'yTi' : [3.0, 2.0],
# 	'zTi' : [3.0, 2.0],
# 	'xTx' : [-3.0, 2.0], # true value 2.7
# 	'yTy' : [-3.0, 2.0], # true value 2.7
# 	'zTz' : [-3.0, 2.0], # true value 2.14
# 	'xTy' : [3.0, 2.0],
# 	'xTz' : [3.0, 2.0],
# 	'yTz' : [3.0, 2.0],
# }

# from results of long QHL, Oct_01/12_08
# 22:48:8 [QML 3] Final Parameters mean and stdev (term  xTi ): [ 0.17888641  0.02239774]
# 22:48:8 [QML 3] Final Parameters mean and stdev (term  yTi ): [ 5.50795523  0.0623826 ]
# 22:48:8 [QML 3] Final Parameters mean and stdev (term  zTi ): [ 0.60514502  0.12197497]
# 22:48:8 [QML 3] Final Parameters mean and stdev (term  xTx ): [-2.98859264  0.12430515]
# 22:48:8 [QML 3] Final Parameters mean and stdev (term  yTy ): [-0.02375341  0.00765409]
# 22:48:8 [QML 3] Final Parameters mean and stdev (term  zTz ): [-0.27888531  0.0200708 ]

# results from QHL previous run which led us to think about kHz params for hyperfine.. (email to Seb 12 Sep 18)
"""
set_prior_specific_terms = {
	'xTi' : [ 0.17 , 2.0], # TODO Broaden, testing with small dist
	'yTi' : [ 0.77 , 2.0 ],
	'zTi' : [ -0.08 , 2.0],
	'xTx' : [-0.05 , 1.5], # true value 2.7
	'yTy' : [0.08 , 1.5], # true value 2.7
	'zTz' : [-3.9 , 1.5 ], # true value 2.14
	'xTy' : [3.0, 2.0],
	'xTz' : [3.0, 2.0],
	'yTz' : [3.0, 2.0],
}
set_prior_specific_terms = {
	'xTi' : [ 0.5 , 1.5], # TODO Broaden, testing with small dist
	'yTi' : [ 0.5, 1.5 ],
	'zTi' : [ 0.5, 1.5],
	'xTx' : [-2.7, 0.2], # true value 2.7
	'yTy' : [-2.7, 0.2], # true value 2.7
	'zTz' : [-2.1, 0.2], # true value 2.14
	'xTy' : [3.0, 2.0],
	'xTz' : [3.0, 2.0],
	'yTz' : [3.0, 2.0],
}
set_prior_specific_terms = {
	'xTi' : [ 0 , 1.0], # TODO Broaden, testing with small dist
	'yTi' : [ 0 , 1.0 ],
	'zTi' : [ 0 , 1.0],
	'xTx' : [0 , 1.0], # true value 2.7
	'yTy' : [0, 1.0], # true value 2.7
	'zTz' : [0 , 1.0 ], # true value 2.14
	'xTy' : [3.0, 2.0],
	'xTz' : [3.0, 2.0],
	'yTz' : [3.0, 2.0],
}
"""
# random set generated using random.uniform(-10, 10) for purposes of QHL tests
set_prior_specific_terms = {
	'xTi' : [ 5.0, 2.0 ], # TODO Broaden, testing with small dist
	'yTi' : [ 5.0, 2.0 ],
	'zTi' : [ 5.0, 2.0 ],
	'xTx' : [5.0, 2.0], # true value 2.7
	'yTy' : [5.0, 2.0], # true value 2.7
	'zTz' : [3.0, 2.0 ], # true value 2.14
	'xTy' : [5.0, 2.0],
	'xTz' : [5.0, 2.0],
	'yTz' : [5.0, 2.0],
	'x' : [5.0, 2.0],
	'z' : [5.0, 2.0],
	'y' : [5.0, 2.0]
}

set_true_params = {

	'xTi' : 0.7538085315,
	'yTi' : 8.4442484,
	'zTi' : 5.713337168736279,
	'xTx' : 1.9632210928717253,
	'yTy' : 2.7435186090389045,
	'zTz' : 2.43632654,
	'xTy' : 1.6,
	'xTz' : 1.7,
	'yTz' : 1.8,
	'xTxTTx' : 1.2345
}


### Functions ###


def create_plot_probe(
	max_num_qubits = 7, 
	pickle_file = None,
	# plus_probe_for_plot = True,
	# experimental_data=True, 
	# growth_generator=None,
	**kwargs
):
	# import ExpectationValues
	import numpy as np
	# kwargs['test_fill'] = 98
	# print("[createPlotProbe] kwargs", kwargs)
	# print("[createPlotProbe] exp data:", experimental_data )
	# print("[createPlotProbe] ggr:",growth_generator )
	plot_probe_dict = UserFunctions.get_probe_dict(
		# experimental_data = experimental_data, 
		# growth_generator = growth_generator,
		num_probes = 1,
		# plus_probe = plus_probe_for_plot,
		**kwargs
	)
	for k in list(plot_probe_dict.keys()):
		# replace tuple like key returned, with just dimension. 
	    plot_probe_dict[k[1]] = plot_probe_dict.pop(k)


	# plot_probe_dict = {}
	
	# for i in range(1,max_num_qubits):
	# 	if plus_probe_for_plot == True:
	# 		plot_probe_dict[i] = ExpectationValues.n_qubit_plus_state(i)
	# 	else:
	# 		if i==1:
	# 			plot_probe_dict[i] = ExpectationValues.random_probe(i)
	# 		else:
	# 			old_probe = plot_probe_dict[i-1]
	# 			new_probe = ExpectationValues.random_probe(1)
	# 			n_dim_probe = np.kron(old_probe, new_probe)
	# 			plot_probe_dict[i] = n_dim_probe

	if pickle_file is not None:
		import pickle
		pickle.dump(
			plot_probe_dict,
			open(pickle_file, 'wb') 
		)
			


def create_qhl_params(
	true_op, 
	pickle_file=None,
	random_vals=False, 
	rand_min=0, 
	rand_max=5,
	exp_data=0,
	plus_probe_for_plot=False
):
	terms = DataBase.get_constituent_names_from_name(true_op)
	true_params = []

	true_params_dict = {}

	if random_vals is True:
		for term in terms:
			val = random.uniform( rand_min, rand_max) 
			true_params.append( val )
			true_params_dict[term] = val

	else:
		for term in terms:
			try:
				this_true_param = set_true_params[term]
			except:
				this_true_param = random.uniform( rand_min, rand_max)

			true_params.append( this_true_param )
			true_params_dict[term] = this_true_param
			
	true_params_info = {
		'params_list' : true_params,
		'params_dict' : true_params_dict
	}
	if exp_data: 
		# so as not to plot "true" params for exp data
		true_params_info['params_dict'] = None

	true_params_info['true_op'] = true_op

	if pickle_file is not None:
		import pickle
		pickle.dump(
			true_params_info, 
			open(pickle_file, 'wb')
		)

def create_prior(
	true_op, 
	pickle_file=None,
	random_vals=False, 
	sigma=1.5,
	rand_min=0, 
	rand_max=5,
	exp_data=0
):
#	terms = DataBase.get_constituent_names_from_name(true_op)
	specific_terms = {}
	terms = list(set_prior_specific_terms.keys())
	if random_vals is True:
		for term in terms:
			val = random.uniform(rand_min, rand_max)
			specific_terms[term] = [val, sigma]
	else:
		for term in terms:
			try:
				specific_terms[term] = set_prior_specific_terms[term]
			except: 
				# in case term not in set_prior_specific_terms
				val = random.uniform(rand_min, rand_max)
				specific_terms[term] = [val, sigma]
			
	if pickle_file is not None:
		import pickle
		pickle.dump(
			specific_terms, 
			open(pickle_file, 'wb')
		)
			
### Parse arguments from bash
parser = argparse.ArgumentParser(description='Pass files to pickel QHL parameters.')

parser.add_argument(
  '-true', '--true_params_file', 
  help="File to pickle true params list to.",
  type=str,
  default=None
)
parser.add_argument(
  '-rand_t', '--random_true_params', 
  help="Bool: use random true parameters or those defined in this file.",
  type=int,
  default=0
)


parser.add_argument(
  '-prior', '--prior_file', 
  help="File to pickle prior specific terms to.",
  type=str,
  default=None
)
parser.add_argument(
  '-rand_p', '--random_prior_terms', 
  help="Bool: use random true parameters or those defined in this file.",
  type=int,
  default=0
)

parser.add_argument(
  '-op', '--true_op', 
  help="Operator to generate true params and prior for.",
  type=str,
  default='xTiPPyTiPPzTiPPxTxPPyTyPPzTz'
)

parser.add_argument(
  '-exp', '--use_experimental_data', 
  help="Bool: use experimental data or not.",
  type=int,
  default=0
)

parser.add_argument(
  '-ggr', '--growth_generation_rule', 
  help="Generator of new models",
  type=str,
  default=0
)

parser.add_argument(
  '-probe', '--plot_probe_file', 
  help="File to pickle probes against which to plot expectation values.",
  type=str,
  default=None
)
parser.add_argument(
  '-plus', '--force_plus_probe', 
  help="Whether to enforce plots to use |+>^n as probe.",
  type=int,
  default=0
)


arguments = parser.parse_args()
random_true_params = bool(arguments.random_true_params)
random_prior = bool(arguments.random_prior_terms)
exp_data = bool(arguments.use_experimental_data)
growth_generation_rule = arguments.growth_generation_rule
true_operator = UserFunctions.default_true_operators_by_generator[growth_generation_rule]
plot_probe_file = arguments.plot_probe_file
force_plus_probe = bool(arguments.force_plus_probe)

### Call functions to create pickle files. 
## TODO check if these are already present?
if arguments.true_params_file is not None:
	create_qhl_params(
		# true_op = arguments.true_op, 
		true_op = true_operator,
		pickle_file=arguments.true_params_file,
		random_vals=random_true_params, 
		exp_data=exp_data
	)

if arguments.prior_file is not None:
	create_prior(
		# true_op = arguments.true_op,
		true_op = true_operator, 
		pickle_file = arguments.prior_file,
		random_vals = random_prior, 
		exp_data=exp_data
	)

if (
	force_plus_probe == True 
	or 
	exp_data == True
):
	force_plus = True
else:
	force_plus = False


kwargs_for_plot_probe_creation = {
	'true_operator' : true_operator, 
	'growth_generator' : growth_generation_rule,
	'experimental_data' : exp_data,
	'plus_probe_for_plot' : force_plus, 

}

create_plot_probe(
	pickle_file = plot_probe_file,
	max_num_qubits = 10,
	**kwargs_for_plot_probe_creation
)