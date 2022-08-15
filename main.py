import multiprocessing
import numpy as np

from args import ArgsConfig
from utils import Network
from plot import PlotBarHandlder, PlotLinesHandler

FIG = 4

def run_simulation_fc(log_data, args, param_p, param_b):
    net = Network(args, args.random_seed)
    net.simulate()
    if net.get_fc() != 0.0:
        log_data[param_p.index(args.p)][param_b.index(args.T)].append(net.get_fc())

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
        pool.starmap(run_simulation_fc, args_list)

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
             
    if FIG == 4:
        PARAM_P = [0.0, 0.1]
        PARAM_B = [_ for _ in np.arange(1, 2, 0.05)]

        # log_data = [[] for _ in range(len(PARAM_P))]
        # for p_idx in range(len(PARAM_P)):
        #     for b_idx in range(len(PARAM_B)):
        #         manager = multiprocessing.Manager()
        #         log_list = manager.list()
        #         log_data[p_idx].append(log_list)

        # args_list = list()
        # for p in PARAM_P:
        #     for b in PARAM_B:
        #         for rep_idx in range(args.n_replication):
        #             args_tmp = parser.get_args()
        #             args_tmp.p = p
        #             args_tmp.T = b
        #             args_tmp.random_seed = args.random_seed + rep_idx
        #             args_list.append([log_data, args_tmp, PARAM_P, PARAM_B])
        
        # n_cpus = multiprocessing.cpu_count()
        # print("cpu count: {}".format(n_cpus))
        # pool = multiprocessing.Pool(n_cpus+2)
        # pool.starmap(run_simulation_avg_payoff_diff, args_list)

        # for p_idx in range(len(PARAM_P)):
        #     for b_idx in range(len(PARAM_B)):
        #         log_data[p_idx][b_idx] = list(log_data[p_idx][b_idx])
        # print(log_data)

        log_data = [[[-0.8858449687048626], [-0.5389592757561754], [-0.6169471505766211], [-0.4725233840250578], [-0.49724398093135846], [-0.5993484520317445], [-0.57312897623303], [-0.4741323769979706], [-0.7138410734346232], [-0.5882648430135831], [-0.7216830321525585], [-0.6857015344224813], [-0.6567065297229826], [-0.6340976356251922], [-0.6292617476327802], [-0.850066998456791], [-0.6785081114598466], [-0.6771867150684461], [-0.6904305794335412], [-0.6171442295038263]], [[-0.6933884379686646], [-0.434626056133224], [-0.4024019279879205], [-0.3509055234058813], [-0.4187014825849964], [-0.48749891615040575], [-0.35709818276919947], [-0.4215759305354885], [-0.5053455296776042], [-0.4633282954471909], [-0.619906586840556], [-0.5841570074834443], [-0.48098073867113467], [-0.6033314669542573], [-0.6206865785958078], [-0.7991378047338209], [-0.7091745138391099], [-0.6178914525476831], [-0.6717894957814146], [-0.731420884914634]]] 

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
