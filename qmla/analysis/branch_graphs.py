import sys
import os
import numpy as np
import pickle
import itertools
import copy
import scipy
import math
import pandas as pd
import seaborn as sns
import random
import sklearn
import networkx as nx

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.pyplot import GridSpec

import qmla

def plot_qmla_branches(q):
    trees = list(q.trees.values())
    tree = trees[0] # TODO plot for all GR's this instance

    branches = [
        tree.branches[b] for b in 
        sorted(tree.branches.keys())
    ]
    branches = branches[:-1]

    num_branches = len(branches)
    ncols = int(np.ceil(np.sqrt(num_branches))) 
    if ncols == 1:
        ncols = 1
        nrows = 1
        cmap_widths = 0.1
    if ncols == 2:
        ncols = 1
        nrows = 2
        cmap_widths = 0.1
    else:
        nrows = int(np.ceil(num_branches / ncols))  
        cmap_widths = 0.1
    total_ncols = ncols + 2 # extra for cmaps

    plt.clf()
    fig = plt.figure( 
        figsize=(15, 10),
        constrained_layout=True
    )
    widths = [1]*ncols
    widths.extend([cmap_widths, cmap_widths])
    label_fontsize = 20

    gs = GridSpec(
        nrows = nrows,
        ncols = total_ncols,
        width_ratios = widths
    )

    # colour maps
    f_score_cmap = plt.cm.get_cmap('Blues')
    bf_cmap = plt.cm.get_cmap('jet')
    min_bf = q.bayes_factors_df.log10_bayes_factor.min()
    max_bf = q.bayes_factors_df.log10_bayes_factor.max()
    norm = plt.Normalize(vmin = min_bf, vmax = max_bf)
    bf_cmapper = plt.cm.ScalarMappable(norm=norm, cmap=bf_cmap)
    bf_cmapper.set_array([]) # still no idea what this is for??

    row = 0
    col = 0 

    min_seen_bf = 0
    max_seen_bf = 0

    for branch in branches:
        
        ax = fig.add_subplot(gs[row, col])
        
        models = branch.models.keys()
        pairs = branch.pairs_to_compare

        graph = nx.Graph()
        for m in models:
            graph.add_node(
                m, 
                model_id=int(m), 
                model_name=branch.models[m],
                f_score = q.model_f_scores[m],
                colour = f_score_cmap(q.model_f_scores[m]),
                longest_path_to_any_target = 0
            )

        for edge in pairs:
            e = (min(edge), max(edge)) # edges go A->B low -> high
            bf = q.all_bayes_factors[e[0]][e[1]][-1]
            lbf = np.log10( bf ) 
            colour = bf_cmapper.to_rgba(lbf)
            graph.add_edge(
                e[0], e[1],
                log_bf = lbf,
                colour = colour
            )    



        pos = nx.spring_layout(graph)
        labels = nx.get_node_attributes(graph, 'model_id')
        node_colours = [ graph.nodes[m]['colour'] for m in models]
        edge_colours = [ graph.edges[e]['colour'] for e in graph.edges ]

        nx.draw_networkx_nodes(
            graph, 
            pos, 
            alpha = 0.7,
            node_color = node_colours,
            node_size = 800,
            ax = ax
        )
        nx.draw_networkx_labels(graph,pos,labels,font_size=24, ax = ax)

        nx.draw_networkx_edges(
            graph, 
            pos, 
            edgelist = graph.edges,
            edge_color = edge_colours,
            ax = ax,
            alpha = 1
        )
        
        
        # summarise this graph in a text box
        node_edges = { n : len(graph.edges(n)) for n in graph.nodes}
        lowest_connectivity = min( node_edges.values() )
        highest_connectivity = max( node_edges.values() )

        for n in graph:
            for target in graph:
                if n != target:
                    shortest_path = nx.shortest_path_length(
                        graph, 
                        source = n, 
                        target = target
                    )

                    this_node_current_longest_path = graph.nodes[n]['longest_path_to_any_target']
                    if shortest_path  > this_node_current_longest_path:
                        graph.nodes[n]['longest_path_to_any_target'] = shortest_path

        distance_between_nodes = [ graph.nodes[n]['longest_path_to_any_target'] for n in graph.nodes]                

        lowest_distance_between_nodes = min(distance_between_nodes)
        highest_distance_between_nodes = max(distance_between_nodes)

        summary = " {} models \n {} edges.\n ${} \leq  C \leq{}$\n $d \leq {}$".format(
            len(graph.nodes),
            len(graph.edges), 
            lowest_connectivity, highest_connectivity, 
            highest_distance_between_nodes
        )
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        
        ax.text(-0.15, 0.85, summary, transform=ax.transAxes, fontsize = 14, bbox=props)
        ax.axis('off')
        ax.set_title("Branch {}".format(branch.branch_id), fontsize=label_fontsize)
        
        col += 1
        if col == ncols:
            col = 0
            row += 1

    # BF cmap
    ax = fig.add_subplot(gs[:, total_ncols-2])
    fig.colorbar(bf_cmapper, cax = ax)
    ax.set_title(r"$log_{10}(BF)$", fontsize=label_fontsize)

    # F score
    ax = fig.add_subplot(gs[:, total_ncols-1])

    sm = plt.cm.ScalarMappable(
        cmap = f_score_cmap, 
        norm=plt.Normalize(vmin=0, vmax=1)
    )
    sm.set_array([])
    fig.colorbar(sm, cax=ax, orientation='vertical')
    ax.set_title(r"F-score", fontsize=label_fontsize)

    # Save figure
    fig.savefig(
        os.path.join(q.qmla_controls.plots_directory, 
        'branch_graphs.png')
    )