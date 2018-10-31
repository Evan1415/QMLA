##### ---------- -------------------- #####  
"""
This file allows users to inject their own functionality into QMD.
To specify a new set of rules, QMD must be provided some flags
- growth_generation_rule: 
	which tree growth mechanism to use
- measurement_type: 
	which measurement ought to be applied to the quantum system, 
	corresponding to experimental measurements/other 
	constraints of your system. 

These each require new functionality to be used
(or else to use existing functionality). In either case, 
you must inform QMD what functions to use for your case. 
Below are wrapper functions which are called within QMD. 
The functions these pass into must be altered for new QMD applications.
- Tell each of the dictionaries below the 
	corresponding functions to your growth and measurement rules. 
- These must be written to take the parameters QMD passes, 
	some inputs are essential and some optional. 
	Essential inputs for each newly written function
	are explained inline below. 
"""
##### ---------- -------------------- #####  



import ModelGeneration 
import ModelNames 
import ExpectationValues

def time_seconds():
    import datetime
    now =  datetime.date.today()
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    second = datetime.datetime.now().second
    time = str(str(hour)+':'+str(minute)+':'+str(second))
    return time

def log_print(to_print_list, log_file):
    identifier = str(str(time_seconds()) +" [USER FUNCTIONS]")
    if type(to_print_list)!=list:
        to_print_list = list(to_print_list)

    print_strings = [str(s) for s in to_print_list]
    to_print = " ".join(print_strings)
    with open(log_file, 'a') as write_log_file:
        print(identifier, str(to_print), file=write_log_file, flush=True)


##### ---------- -------------------- #####  
# Measurement/Expectation Values
##### ---------- -------------------- #####  

expec_val_function_dict = {
	# measurement_type : expectation_value_function_for_that_meas
    'full_access' : 
    	ExpectationValues.expectation_value, 
    'hahn' : 
    	ExpectationValues.hahn_evolution,
    'trace_all_but_first' : 
    	ExpectationValues.traced_expectation_value_project_one_qubit_plus
}


##### ---------- -------------------- #####  
# Model Generation
# Here you must also define how many growth steps to allow 
# the decision tree to undergo, in max_spawn_depth_info. 
##### ---------- -------------------- #####  

max_spawn_depth_info = {
    'qhl_TEST' : 2, 
    'simple_ising' : 1,
    'hyperfine' : 3,
    'ising_non_transverse' : 5,
    'ising_transverse' : 11,
    'hyperfine_like' : 8,
    'two_qubit_ising_rotation' : 2,
    'two_qubit_ising_rotation_hyperfine' : 5, # for dev, should be 5 #TODO put back
    'two_qubit_ising_rotation_hyperfine_transverse' : 8,
    'test_multidimensional' : 10, 
    'test_return_champs' : 3,
    'non_interacting_ising' : 3,
    'non_interacting_ising_single_axis' : 3,
    'interacting_nearest_neighbour_ising' : 3,
    'interacing_nn_ising_fixed_axis' : 5,
}

model_generation_functions = {
	# growth_generation_rule : growth_function
    'simple_ising' : 
    	ModelGeneration.simple_ising,
    'ising_non_transverse' : 
    	ModelGeneration.ising_non_transverse,
    'ising_transverse' : 
    	ModelGeneration.ising_transverse,
    'two_qubit_ising_rotation_hyperfine' : 
    	ModelGeneration.hyperfine_like,
    'two_qubit_ising_rotation_hyperfine_transverse' : 
    	ModelGeneration.hyperfine_like,
    'hyperfine_like' : 
    	ModelGeneration.hyperfine_like,
    'test_multidimensional' : 
    	ModelGeneration.test_multidimensional,
	'test_return_champs' : 
		ModelGeneration.existing_branch_champs_test,
	'non_interacting_ising': 
		ModelGeneration.non_interacting_ising,
	'non_interacting_ising_single_axis':
		ModelGeneration.non_interacting_ising_single_axis,
	'interacting_nearest_neighbour_ising': 
		ModelGeneration.interacting_nearest_neighbour_ising,
	'interacing_nn_ising_fixed_axis':
		ModelGeneration.interacting_nearest_neighbour_ising

}

##### ---------- -------------------- #####  
# Functions to check whether the tree being learned is completed. 
# E.g. by checking if it is at maximum depth (spawn_depth).
##### ---------- -------------------- #####  

tree_finished_functions = {
	None : 
		ModelGeneration.spawn_depth_check
}


##### ---------- -------------------- #####  
# Mapping model name strings to branch numbers
##### ---------- -------------------- #####  

name_branch_map_functions = {
	# growth_generation_rule : latex_mapping_function
	None : 
		ModelNames.branch_is_num_params,
	'two_qubit_ising_rotation_hyperfine' : 
		ModelNames.branch_is_num_params, 
	'two_qubit_ising_rotation_hyperfine_transverse' : 
		ModelNames.branch_is_num_params, 
	'test_return_champs' :
		ModelNames.branch_is_num_params,
	'non_interacting_ising' :
		ModelNames.branch_is_num_dims,
	'interacting_nearest_neighbour_ising' : 
		ModelNames.branch_is_num_dims,
	'non_interacting_ising_single_axis':
		ModelNames.branch_is_num_dims,
	'interacing_nn_ising_fixed_axis':
		ModelNames.branch_is_num_dims
}



##### ---------- -------------------- #####  
# Mapping model name strings to latex representation
##### ---------- -------------------- #####  

latex_naming_functions = {
	# growth_generation_rule : latex_mapping_function

	None : 
		ModelNames.interaction_latex_name,
	# None : 
	# 	ModelNames.default_latex_wrapping,

	'two_qubit_ising_rotation_hyperfine' : 
		ModelNames.latex_name_ising, 
	'two_qubit_ising_rotation_hyperfine_transverse' : 
		ModelNames.latex_name_ising, 
	# 'test_return_champs' :
	# 	ModelNames.default_latex_wrapping,
	# 'interacting_nearest_neighbour_ising' : 
	# 	ModelNames.nearest_neighbour_ising_latex_name
}


##### ---------- -------------------- #####  
# All possible models according to this growth rule
# primarily just for tree plotting
##### ---------- -------------------- #####  

all_models_functions = {
	None : 
		ModelNames.ising_terms_rotation_hyperfine,
	'two_qubit_ising_rotation_hyperfine' : 
		ModelNames.ising_terms_rotation_hyperfine, 
	'two_qubit_ising_rotation_hyperfine_transverse' : 
		ModelNames.ising_terms_full_list, 
	'test_return_champs' :
		ModelNames.test_return_champs_ALL_MODELS,
	'non_interacting_ising' :
		ModelNames.non_interacting_ising_all_names,
	'non_interacting_ising_single_axis':
		ModelNames.non_interacting_ising_all_names,
	'interacting_nearest_neighbour_ising':
		ModelNames.interacting_ising_nearest_neighbours_all_names,
	'interacing_nn_ising_fixed_axis':
		ModelNames.interacting_ising_nearest_neighbours_all_names  
}


initial_models = {
	None :
		['x', 'y', 'z'],
	'two_qubit_ising_rotation_hyperfine' :
		['xTi', 'yTi', 'zTi'],
	'two_qubit_ising_rotation_hyperfine_transverse' : 
		['xTi', 'yTi', 'zTi'],
	'interacting_nearest_neighbour_ising' :
		['xTx', 'yTy', 'zTz'],
	'hyperfine_like' : 
		['xTi', 'yTi', 'zTi'],
	'interacing_nn_ising_fixed_axis' :
		['xTx', 'yTy', 'zTz']
}

##### ---------- -------------------- #####  
# Wrapper functions 
##### ---------- -------------------- #####  


def new_model_generator(generator, **kwargs):
    model_func = model_generation_functions[generator]
    # print("[User funcs] Using model generation function:", model_func)
    return model_func(**kwargs)

def expectation_value_wrapper(method, **kwargs):       
    # method means measurement_type flag, provided to QMD
    # print("method:", method)
    expectation_value_function = expec_val_function_dict[method]
    return expectation_value_function(**kwargs)


def max_spawn_depth(generator, log_file):
    if generator not in max_spawn_depth_info:
        log_print(
        	[
        	"Generator not recognised; \
        	does not have maximum spawn depth or \
        	generation function"
        	], 
        	log_file
    	)
    else:
        return max_spawn_depth_info[generator]



def tree_finished(generator, **kwargs):
	try:
		tree_finished_check = tree_finished_functions[generator]
	except:
		tree_finished_check = tree_finished_functions[None]

	tree_completed = tree_finished_check(
		generator = generator, 
		max_spawn_depth_info = max_spawn_depth_info,
		**kwargs
	)
	# print("[tree finished] func:", tree_finished_check)
	# print("tree completed:", tree_completed)
	return tree_completed 		



def get_latex_name(
    name, 
    growth_generator=None,
    **kwargs
):
	try:
		# if mapping doesn't work, default to just wrap in $__$. 
		latex_mapping = latex_naming_functions[growth_generator]
		latex_representation = latex_mapping(name, **kwargs)
	except:
		latex_mapping = latex_naming_functions[None]
		latex_representation = latex_mapping(name, **kwargs)
	# print("Latex Mapping used", latex_mapping)

	return latex_representation



def get_all_model_names(
	growth_generator = None,
	**kwargs
):
	all_models = all_models_functions[growth_generator]
	# print("all model function:", all_models)
	return all_models(**kwargs)



def get_name_branch_map(
    latex_mapping_file, 
    growth_generator=None,
    **kwargs
):
	try:
		# if mapping doesn't work, default to just wrap in $__$. 
		branch_mapping = name_branch_map_functions[growth_generator]
		name_branch_map = branch_mapping(
			latex_mapping_file=latex_mapping_file, 
			**kwargs
		)
	except:
		branch_mapping = name_branch_map_functions[None]
		name_branch_map = branch_mapping(
			latex_mapping_file=latex_mapping_file, 
			**kwargs
		)
	# print("Latex Mapping used", branch_mapping)

	return name_branch_map


def get_initial_op_list(
	growth_generator=None, 
	log_file='qmd.log',
	**kwargs
):
	try:
		initial_ops = initial_models[growth_generator]
	except:
		initial_ops = initial_models[None]
		log_print(
			[
			"Initial operators not known for generator", 
			growth_generator, 
			". Defaulting to:", initial_ops
			],
			log_file
		)
	return initial_ops
