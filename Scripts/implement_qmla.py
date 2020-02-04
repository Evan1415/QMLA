from __future__ import print_function  # so print doesn't show brackets
import os as os
import warnings
import numpy as np
import itertools as itr
import matplotlib.pyplot as plt
import sys as sys
import pandas as pd
import warnings
import time as time
import random
import pickle
pickle.HIGHEST_PROTOCOL = 2

sys.path.append("..")
import qmla
from qmla import database_framework
from qmla.quantum_model_learning_agent import QuantumModelLearningAgent  # QMD class in Library
from qmla import redis_settings as rds

# Parse input variables to use in QMD; store in class global_variables.
global_variables = qmla.parse_cmd_line_args(sys.argv[1:])
growth_class = global_variables.growth_class

###  START QMD ###
start = time.time()

"""
Set up and functions.
"""


def time_seconds():
    import datetime
    now = datetime.date.today()
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    second = datetime.datetime.now().second
    time = str(str(hour) + ':' + str(minute) + ':' + str(second))
    return time


def log_print(to_print_list, log_file):
    identifier = str(str(time_seconds()) + " [EXP]")
    if not isinstance(to_print_list, list):
        to_print_list = list(to_print_list)

    print_strings = [str(s) for s in to_print_list]
    to_print = " ".join(print_strings)
    with open(log_file, 'a') as write_log_file:
        print(identifier,
              str(to_print),
              file=write_log_file,
              flush=True
              )


# Note this should usually be False, True just for testing/some specific plots.
store_particles_weights = False

log_file = global_variables.log_file
qle = global_variables.do_qle  # True for QLE, False for IQLE

growth_class.generate_probes(
    experimental_data=global_variables.use_experimental_data,
    noise_level=global_variables.probe_noise_level,
    minimum_tolerable_noise=0.0,
)

system_probes = growth_class.probes_system
simulator_probe_dict = growth_class.probes_simulator
log_print(
    [
        "Generated probe dict from growth class"
    ],
    log_file=log_file
)

probes_dir = str(
    global_variables.results_directory
    + 'training_probes/'
)
if not os.path.exists(probes_dir):
    try:
        # store probes used for training by the first QMLA instance to be
        # generated.
        os.makedirs(probes_dir)
        system_probes_path = str(
            probes_dir
            + 'system_probes'
            + '.p'
        )
        pickle.dump(
            system_probes,
            open(system_probes_path, 'wb')
        )
        simulator_probes_path = str(
            probes_dir
            + 'simulator_probes'
            + '.p'
        )
        pickle.dump(
            simulator_probe_dict,
            open(simulator_probes_path, 'wb')
        )
    except BaseException:
        # if already exists (ie created by another QMD since if test ran...)
        pass

if global_variables.use_experimental_data: 
    dataset = global_variables.dataset
    log_print(
        [
            "[EXP] For  growth rule {}; use dataset {}".format(
                global_variables.growth_generation_rule, dataset
            )
        ],
        log_file=log_file
    )
    experimental_measurements_dict = pickle.load(
        open(str('../Launch/Data/' + dataset), 'rb')
    )
    expec_val_plot_max_time = max(
        list(experimental_measurements_dict.keys())
    )
    # expec_val_plot_max_time = global_variables.data_max_time
else:
    expec_val_plot_max_time = global_variables.data_max_time
    experimental_measurements_dict = None

num_datapoints_to_plot = 300
plot_lower_time = 0
plot_upper_time = growth_class.max_time_to_consider
plot_number_times = num_datapoints_to_plot
raw_times = list(np.linspace(
    plot_lower_time,
    plot_upper_time,
    plot_number_times + 1)
)
plot_times = [np.round(a, 2) for a in raw_times]
plot_times = sorted(plot_times)
if global_variables.use_experimental_data == True:
    plot_times = sorted(
        list(experimental_measurements_dict.keys())
    )

# do not get initial model list directly from growth rule in case using further qhl mode
first_layer_models = growth_class.initial_models 
log_print(
    [
        "[Exp] Retrieved initial op list from growth class"
    ],
    log_file=log_file
)

true_op = global_variables.true_operator
true_num_qubits = database_framework.get_num_qubits(true_op)
true_op_list = database_framework.get_constituent_names_from_name(true_op)
true_op_matrices = [database_framework.compute(t) for t in true_op_list]
num_params = len(true_op_list)
true_expectation_value_path = global_variables.true_expec_path
true_ham = global_variables.true_hamiltonian

if os.path.isfile(true_expectation_value_path) == False:
    true_expec_values = {}
    plot_probe_dict = pickle.load(
        open(global_variables.probes_plot_file, 'rb')
    )
    probe = plot_probe_dict[true_num_qubits]
    log_print(
        [
            "for generating true data.",
            "\n\tprobe:\n", repr(probe),
            "\n\t(with 1-norm:)", np.abs(1 - np.linalg.norm(probe)),
            "\n\n\ttrue_ham:\n", repr(true_ham)
        ],
        log_file
    )
    if global_variables.use_experimental_data == True:
        true_expec_values = experimental_measurements_dict
    else:
        log_print(
            [
                "Getting true expectation values (for plotting)"
                "\nTimes computed(len {}): {}\n".format(
                    len(plot_times), plot_times
                )
            ],
            log_file
        )
        for t in plot_times:
            try:
                true_expec_values[t] = (
                    growth_class.expectation_value(
                        ham=true_ham,
                        t=t,
                        state=probe,
                        log_file=log_file,
                        log_identifier='[Exp - Getting true expec vals for plotting]'
                    )
                )

            except BaseException:
                log_print(
                    [
                        "failure for",
                        "\ntrue ham:", repr(true_ham),
                        "\nprobe:", repr(probe),
                        "t=", t
                    ],
                    log_file
                )
                raise

    pickle.dump(
        true_expec_values,
        open(true_expectation_value_path, 'wb')
    )

else:
    true_expec_values = pickle.load(
        open(true_expectation_value_path, 'rb')
    )

model_priors = None

if global_variables.further_qhl == True:

    qmd_results_model_scores_csv = str(
        global_variables.results_directory
        + 'average_priors.p'
    )
    print("QMD results CSV in ", qmd_results_model_scores_csv)
    model_priors = pickle.load(
        open(
            qmd_results_model_scores_csv,
            'rb'
        )
    )
    log_print(
        ["Futher QHL. Model_priors:\n", model_priors],
        log_file
    )
    first_layer_models = list(model_priors.keys())
    further_qhl_models = list(model_priors.keys())


num_ops = len(first_layer_models)
do_qhl_plots = False  # testing posterior transition # TODO turn off usually

results_directory = global_variables.results_directory
long_id = global_variables.long_id

log_print(
    [
        "\n QMD id", global_variables.qmd_id,
        " on host ", global_variables.host_name,
        "and port", global_variables.port_number,
        "has seed", rds.get_seed(global_variables.host_name,
                                 global_variables.port_number, global_variables.qmd_id,
                                 print_status=True),
        "\n", global_variables.num_particles,
        " particles for", global_variables.num_experiments,
        "experiments and ", global_variables.num_times_bayes,
        "bayes updates\n Gaussian=", global_variables.gaussian,
        "\n RQ=", global_variables.use_rq, "RQ log:",
        global_variables.log_file, "\n Bayes CSV:",
        global_variables.cumulative_csv
    ],
    log_file
)

"""
Launch and run QMD
"""

generators = [
    global_variables.growth_generation_rule,
]

generators.extend(
    global_variables.alternative_growth_rules
)
generators = list(set(generators))

log_print(
    [
        "Generators:", generators
    ],
    log_file

)

qmd = QuantumModelLearningAgent(
    global_variables=global_variables,
    generator_list=generators,
    first_layer_models=first_layer_models,
    probe_dict=system_probes,
    sim_probe_dict=simulator_probe_dict,
    model_priors=model_priors,
    experimental_measurements=experimental_measurements_dict,
    plot_times=plot_times,
)

if global_variables.qhl_test:
    qmd.run_quantum_hamiltonian_learning()
    log_print(
        [
            "QHL complete",
        ],
        log_file
    )
    if global_variables.pickle_qmd_class:
        log_print(
            [
                "QMD complete. Pickling result to",
                global_variables.class_pickle_file
            ], log_file
        )
        qmd.delete_unpicklable_attributes()
        with open(global_variables.class_pickle_file, "wb") as pkl_file:
            pickle.dump(qmd, pkl_file, protocol=2)

    if global_variables.save_plots:
        try:
            log_print(
                [
                    "Plotting parameter estimates",
                ],
                log_file
            )
            qmd.plot_parameter_learning_single_model(
                true_model=True,
                save_to_file=str(
                    global_variables.plots_directory +
                    'qhl_parameter_estimates_' +
                    str(global_variables.long_id) +
                    '.png'
                )
            )
        except BaseException:
            pass

        try:
            log_print(
                [
                    "Plotting volumes",
                ],
                log_file
            )
            qmd.plot_volume_after_qhl(
                save_to_file=str(
                    global_variables.plots_directory +
                    'qhl_volume_' +
                    str(global_variables.long_id) +
                    '.png'
                )
            )
        except BaseException:
            pass
        log_print(
            [
                "Plotting Quadratic Losses",
            ],
            log_file
        )

        qmd.plot_branch_champs_quadratic_losses(
            save_to_file=str(
                global_variables.plots_directory +
                'qhl_quadratic_loss_'
                + str(global_variables.long_id) + '.png'
            )
        )

        true_mod_instance = qmd.get_model_storage_instance_by_id(
            qmd.true_model_id
        )

    log_print(
        [
            "Plotting Dynamics",
        ],
        log_file
    )
    qmd.plot_branch_champions_dynamics(
        include_bayes_factors_in_dynamics_plots=False,
        include_param_estimates_in_dynamics_plots=True,
        include_times_learned_in_dynamics_plots=True,
        save_to_file=str(
            global_variables.plots_directory +
            'dynamics_' +
            str(global_variables.long_id) +
            '.png'
        )
    )
    log_print(
        [
            "Finished plotting dynamics",
        ],
        log_file
    )

    true_mod = qmd.get_model_storage_instance_by_id(
        qmd.true_model_id
    )
    extend_dynamics_plot_times = [
        t * 2 for t in qmd.times_to_plot
    ]
    print(
        "[Exp.py - QHL]",
        "Computing more expectation values"
    )
    true_mod.compute_expectation_values(
        times=extend_dynamics_plot_times
    )

    qmd.plot_branch_champions_dynamics(
        model_ids=[qmd.true_model_id],
        include_bayes_factors_in_dynamics_plots=False,
        include_param_estimates_in_dynamics_plots=False,
        include_times_learned_in_dynamics_plots=False,
        save_to_file=str(
            global_variables.plots_directory +
            'extended_dynamics_' +
            str(global_variables.long_id) +
            '.png'
        )
    )

    results_file = global_variables.results_file
    pickle.dump(
        qmdchampion_results,
        open(results_file, "wb"),
        protocol=2
    )

elif (
    global_variables.further_qhl == True
    or global_variables.multiQHL == True
):

    if global_variables.multiQHL == True:
        qhl_models = growth_class.qhl_models
        # output_prefix = 'multi_qhl_'
        output_prefix = ''  # TODO make so that this can have an output prefix

    else:
        qhl_models = further_qhl_models
        output_prefix = 'further_qhl_'

    log_print(
        [
            "Launching QHL with multiple models: {}".format(qhl_models)
        ],
        log_file
    )
    qmd.run_quantum_hamiltonian_learning_multiple_models(
        model_names=qhl_models
    )
    # model_ids = list(range(qmd.highest_model_id))
    model_ids = [
        database_framework.model_id_from_name(
            db=qmd.db,
            name=mod
            # ) for mod in further_qhl_models
        ) for mod in qhl_models
    ]

    qmd.plot_branch_champions_dynamics(
        save_to_file=str(
            global_variables.plots_directory +
            'dynamics_' +
            str(global_variables.long_id) +
            '.png'
        )
    )

    if global_variables.pickle_qmd_class:
        log_print(
            [
                "QMD complete. Pickling result to",
                global_variables.class_pickle_file
            ],
            log_file
        )
        qmd.delete_unpicklable_attributes()
        with open(global_variables.class_pickle_file, "wb") as pkl_file:
            pickle.dump(qmd, pkl_file, protocol=2)

    # results_file = global_variables.results_file

    for mid in model_ids:
        mod = qmd.get_model_storage_instance_by_id(mid)
        name = mod.Name

        results_file = str(
            global_variables.results_directory +
            output_prefix +
            'results_' +
            str(name) + '_' +
            str(global_variables.long_id) +
            '.p'
        )
        print("[Exp] results file:", results_file)

        pickle.dump(
            mod.results_dict,
            open(results_file, "wb"),
            protocol=2
        )


else:
    # qmd.runRemoteQMD(num_spawns=3) #  Actually run QMD
    qmd.run_complete_qmla(num_spawns=3)  # Actually run QMD
    print(" \n\n------QMD learned ------\n\n")

    """
    Tidy up and analysis.
    """
    expec_value_mods_to_plot = []
    try:
        expec_value_mods_to_plot = [qmd.true_model_id]
    except BaseException:
        pass
    expec_value_mods_to_plot.append(qmd.champion_model_id)

    print("plotExpecValues")
    # qmd.plotExpecValues(
    #     model_ids = expec_value_mods_to_plot, # hardcode to see full model for development
    #     times=plot_times,
    #     max_time = expec_val_plot_max_time, #in microsec
    #     t_interval=float(expec_val_plot_max_time/num_datapoints_to_plot),
    #     save_to_file=str(
    #     global_variables.plots_directory+
    #     'expec_values_'+str(global_variables.long_id)+'.png')
    # )
    if global_variables.growth_generation_rule == 'NV_centre_experiment_debug':
        plot_dynamics_all_models = True
    else:
        plot_dynamics_all_models = False
    qmd.plot_branch_champions_dynamics(
        all_models=plot_dynamics_all_models,
        save_to_file=str(
            global_variables.plots_directory +
            'dynamics_' +
            str(global_variables.long_id) +
            '.png'
        )
    )

    champ_mod = qmd.get_model_storage_instance_by_id(
        qmd.champion_model_id
    )
    extend_dynamics_plot_times = [
        t * 2 for t in qmd.times_to_plot
    ]
    print(
        "[Exp.py - QHL]",
        "Computing more expectation values"
    )
    champ_mod.compute_expectation_values(
        times=extend_dynamics_plot_times
    )

    qmd.plot_branch_champions_dynamics(
        model_ids=[qmd.champion_model_id],
        include_bayes_factors_in_dynamics_plots=False,
        include_param_estimates_in_dynamics_plots=False,
        include_times_learned_in_dynamics_plots=False,
        save_to_file=str(
            global_variables.plots_directory +
            'extended_dynamics_' +
            str(global_variables.long_id) +
            '.png'
        )
    )

    if global_variables.save_plots:
        try:
            print("plot_branch_champs_volumes")
            qmd.plot_branch_champs_volumes(
                save_to_file=str(
                    global_variables.plots_directory +
                    'volumes_all_models_' + str(global_variables.long_id) + '.png')
            )
            print("plotExpecValues2")
            qmd.plot_branch_champs_volumes(
                branch_champions=True,
                save_to_file=str(global_variables.plots_directory +
                                 'volumes_branch_champs_' + str(global_variables.long_id) +
                                 '.png')
            )
            print("plotQuadLoss")
            qmd.plot_branch_champs_quadratic_losses(
                save_to_file=str(
                    global_variables.plots_directory +
                    'quadratic_loss_' + str(global_variables.long_id) +
                    '.png'
                )
            )
        except BaseException:
            print("Couldn't plot all individual QMD plots.")

        true_op_known = False
        try:
            if qmd.true_model_id:
                true_op_known = True
        except BaseException:
            true_op_known = False

        if true_op_known == True:
            # if QMD has knowledge of the "true" model, then plot params
            try:
                print("plot_parameter_learning_single_model")
                qmd.plot_parameter_learning_single_model(
                    model_id=qmd.true_model_id,
                    save_to_file=str(
                        global_variables.plots_directory +
                        'true_model_parameter_estimates_' +
                        str(global_variables.long_id) +
                        '.png'
                    )
                )
            except BaseException:
                print(
                    "Failed to plot parameter estimates for true model:",
                    qmd.true_model_name
                )

            if qmd.champion_model_id != qmd.true_model_id:
                try:
                    print("plot_parameter_learning_single_model champ id != true id")
                    qmd.plot_parameter_learning_single_model(
                        model_id=qmd.champion_model_id,
                        save_to_file=str(global_variables.plots_directory +
                                         'champ_model_parameter_estimates_' + str(global_variables.long_id) +
                                         '.png')
                    )
                except BaseException:
                    print(
                        "Failed to plot parameter estimates for ",
                        "champ model:",
                        qmd.champion_model_id
                    )

        else:
            try:
                print("else plot_parameter_learning_single_model")
                qmd.plot_parameter_learning_single_model(
                    model_id=qmd.champion_model_id,
                    save_to_file=str(global_variables.plots_directory +
                                     'champ_model_parameter_estimates_' + str(global_variables.long_id) +
                                     '.png')
                )
            except BaseException:
                print(
                    "Failed to plot parameter estimates for champ model:",
                    qmd.champion_model_id
                )

        """
        # TODO radar plot not working - when used with RQ ???
        # not finding TrueModelID when using ising_hyperfine generation rule
        qmd.plot_qmla_radar_scores(
            save_to_file=str(
            global_variables.plots_directory+
            'radar_'+ str(global_variables.long_id)+ '.png')
        )
        """
        print("store_bayes_factors_to_csv")

        qmd.store_bayes_factors_to_csv(
            save_to_file=str(
                global_variables.results_directory +
                'bayes_factors_' + str(global_variables.long_id) + '.csv'
            ),
            names_ids='latex'
        )

        # TODO generalise so tree diagram can be used in all cases
        # currently only useful for Ising growth 2 qubits.
        try:
            print("plot_qmla_tree")
            qmd.plot_qmla_tree(
                only_adjacent_branches=False,
                save_to_file=str
                (global_variables.plots_directory +
                 'tree_diagram_' +
                 str(global_variables.long_id) +
                 '.png')
            )
        except BaseException:
            print("Failed to plot tree for ", global_variables.long_id)
            raise

        try:
            print("plot_r_squared_by_epoch_for_model_list")
            qmd.plot_r_squared_by_epoch_for_model_list(
                save_to_file=str(
                    global_variables.plots_directory +
                    'r_squared_by_epoch_' + str(global_variables.long_id) +
                    '.png'
                )
            )
        except BaseException:
            log_print(
                [
                    "Failed to plot R squared vs epoch.",
                    "Probably a problem caused by introducing rescaling",
                    "resources based on num qubits etc"
                ],
                log_file
            )

    if (
        global_variables.pickle_qmd_class
        # or
        # global_variables.true_operator == qmd.champion_name_latex
    ):
        log_print(["QMD complete. Pickling result to",
                   global_variables.class_pickle_file], log_file
                  )
        # pickle in cases where true model found
        qmd.delete_unpicklable_attributes()
        with open(global_variables.class_pickle_file, "wb") as pkl_file:
            pickle.dump(qmd, pkl_file, protocol=2)

    # TODO generalise so tree diagram can be used in all cases
    # currently only useful for Ising growth 2 qubits.
    qmd.store_bayes_factors_to_shared_csv(
        bayes_csv=str(global_variables.cumulative_csv)
    )

    results_file = global_variables.results_file
    pickle.dump(
        qmd.champion_results,
        open(results_file, "wb"),
        protocol=2
    )

end = time.time()
log_print(["Time taken:", end - start], log_file)
log_print(["END: QMD id", global_variables.qmd_id, ":",
           global_variables.num_particles, " particles;",
           global_variables.num_experiments, "exp; ",
           global_variables.num_times_bayes,
           "bayes. Time:", end - start
           ],
          log_file
          )

print("QMD finished - results in:", global_variables.results_directory)
