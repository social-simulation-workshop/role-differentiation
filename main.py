import os
import sys
import multiprocessing
from matplotlib.pyplot import figure
import numpy as np

from args import ArgsConfig
from utils import Network
from plot import PlotBarHandlder

PARAM_P = [0.0, 0.01, 0.1, 1.0]
PARAM_B = [1.2, 1.4, 1.6, 1.8]

def run_simulation(log_data, args):
    net = Network(args, args.random_seed)
    net.simulate()
    if net.get_fc() != 0.0:
        log_data[PARAM_P.index(args.p)][PARAM_B.index(args.T)].append(net.get_fc())


if __name__ == "__main__":
    parser = ArgsConfig()
    args = parser.get_args()

    log_data = [[] for _ in range(len(PARAM_P))]
    for p_idx in range(len(PARAM_P)):
        for b_idx in range(len(PARAM_B)):
            manager = multiprocessing.Manager()
            log_list = manager.list()
            log_data[p_idx].append(log_list)

    args_list = list()
    for p in PARAM_P:
        for b in PARAM_B:
            for rep_idx in range(args.n_replication):
                args_tmp = parser.get_args()
                args_tmp.p = p
                args_tmp.T = b
                args_tmp.random_seed = args.random_seed + rep_idx
                args_list.append([log_data, args_tmp])
    
    n_cpus = multiprocessing.cpu_count()
    print("cpu count: {}".format(n_cpus))
    pool = multiprocessing.Pool(n_cpus+2)
    pool.starmap(run_simulation, args_list)

    for p_idx in range(len(PARAM_P)):
        for b_idx in range(len(PARAM_B)):
            log_data[p_idx][b_idx] = list(log_data[p_idx][b_idx])
    print(log_data)

    p_fcs = np.mean(np.array(log_data), axis=-1)
    
    pbh = PlotBarHandlder(
        title=None,
        xlabel="b",
        ylabel="Fraction of cooperators: fc",
        fn="fig3",
        figure_ratio=1117/1950
    )
    
    colors = ["black", "grey", "silver", "white"]
    assert len(colors) == len(p_fcs) and len(p_fcs) == len(PARAM_P)
    for idx in range(len(colors)):
        pbh.plot_bar(p_fcs[idx], "p={}".format(PARAM_P[idx]), colors[idx])
    pbh.save_fig(PARAM_B, fn_suffix="randSeed_{}_repli_{}".format(args.random_seed, args.n_replication))
             