import multiprocessing
import numpy as np

from args import ArgsConfig
from utils import Network
from plot import PlotBarHandlder, PlotLinesHandler

FIG = 3

def run_simulation_fc(log_list, args):
    net = Network(args, args.random_seed)
    net.simulate()
    if not net.reach_all_d_state():
        log_list.append([net.get_final_fc(), int(net.reach_stationary_state())])

def run_simulation_avg_payoff_diff(log_data, args, param_p, param_b):
    net = Network(args, args.random_seed)
    net.simulate()
    log_data[param_p.index(args.p)][param_b.index(args.T)].append(net.get_avg_payoff_diff())


if __name__ == "__main__":
    parser = ArgsConfig()
    args = parser.get_args()

    if FIG == 3:
        PARAM_P = [0.0, 0.01, 0.1, 1.0]
        PARAM_B = [1.2, 1.4, 1.6, 1.8]

        log_data = [[] for _ in range(len(PARAM_P))]
        log_data = list()
        args_list = list()
        for p_idx, p in enumerate(PARAM_P): 
            log_data.append(list())
            for b_idx, b in enumerate(PARAM_B): 
                manager = multiprocessing.Manager()
                log_list = manager.list()
                log_data[p_idx].append(log_list)

                for rep_idx in range(args.n_replication):
                    args_tmp = parser.get_args()
                    args_tmp.p = p
                    args_tmp.T = b
                    args_tmp.random_seed = args.random_seed + rep_idx
                    args_list.append([log_list, args_tmp])

        n_cpus = multiprocessing.cpu_count()
        print("cpu count: {}".format(n_cpus))
        pool = multiprocessing.Pool(n_cpus+2)
        pool.starmap(run_simulation_fc, args_list)

        for p_idx in range(len(PARAM_P)):
            for b_idx in range(len(PARAM_B)):
                log_data[p_idx][b_idx] = list(log_data[p_idx][b_idx])
        print(log_data)

        p_fcs = np.mean(np.array(log_data)[:, :, :, 0], axis=-1)
        print(p_fcs)
        
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

        p_reach = np.mean(np.array(log_data)[:, :, :, 1], axis=-1)

        pbh_reach = PlotBarHandlder(
            title=None,
            xlabel="b",
            ylabel="Percentage of trails reaching stationary state",
            fn="fig3b",
            figure_ratio=1117/1950
        )
        
        colors = ["black", "grey", "silver", "white"]
        assert len(colors) == len(p_reach) and len(p_reach) == len(PARAM_P)
        for idx in range(len(colors)):
            pbh_reach.plot_bar(p_reach[idx], "p={}".format(PARAM_P[idx]), colors[idx])
        pbh_reach.save_fig(PARAM_B, fn_suffix="randSeed_{}_repli_{}".format(args.random_seed, args.n_replication))
             
    if FIG == 4:
        PARAM_P = [0.0, 0.1]
        PARAM_B = [_ for _ in np.arange(1, 2, 0.05)]

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
                    args_list.append([log_data, args_tmp, PARAM_P, PARAM_B])
        
        n_cpus = multiprocessing.cpu_count()
        print("cpu count: {}".format(n_cpus))
        pool = multiprocessing.Pool(n_cpus+2)
        pool.starmap(run_simulation_avg_payoff_diff, args_list)

        for p_idx in range(len(PARAM_P)):
            for b_idx in range(len(PARAM_B)):
                log_data[p_idx][b_idx] = list(log_data[p_idx][b_idx])
        print(log_data)

        p_diffs = np.mean(np.array(log_data), axis=-1)

        plot_handler = PlotLinesHandler(
            xlabel="b",
            ylabel="D-C",
            title=None,
            fn="fig4",
            x_lim=[1.0, 2.0], y_lim=[-2, 10], use_ylim=True,
            x_tick=[1.0, 2.0, 0.2], y_tick=[-2, 10, 2],
            figure_size=7,
            figure_ratio=1601/1966
        )
        plot_handler.plot_scatter(PARAM_B, p_diffs[0], (8, 2), "black")
        plot_handler.plot_scatter(PARAM_B, p_diffs[1], "s", "black", marker_hollow=True)
        plot_handler.save_fig(fn_suffix="randSeed_{}_repli_{}".format(args.random_seed, args.n_replication))
