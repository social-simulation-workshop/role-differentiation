import itertools
import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns

class PlotLinesHandler:
    _ids = itertools.count(0)
    EPSILON = 10**-5

    def __init__(self, title, xlabel, ylabel, fn,
        x_lim, y_lim, x_tick, y_tick, figure_ratio, use_ylim=True, figure_size=12, x_as_kilo=False,
        output_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgfiles")) -> None:
        
        sns.set()
        sns.set_style("white")
        self.id = next(self._ids)

        self.output_dir = output_dir
        self.fn = fn
        self.legend_list = list()

        plt.figure(self.id, figsize=(figure_size, figure_size*figure_ratio), dpi=160)
        if title is not None:
            plt.title(title, fontweight="bold")
        if xlabel is not None:
            plt.xlabel(xlabel)
        if ylabel is not None:
            plt.ylabel(ylabel)

        ax = plt.gca()
        if x_lim is not None:
            ax.set_xlim([x_lim[0], x_lim[1]])
            if x_as_kilo:
                x_tick_label = ["{}K".format(int(i/1000)) for i in np.arange(x_tick[0], x_tick[1]+self.EPSILON, step=x_tick[2])]
                plt.xticks(np.arange(x_tick[0], x_tick[1]+self.EPSILON, step=x_tick[2]), x_tick_label)
            else:
                plt.xticks(np.arange(x_tick[0], x_tick[1]+self.EPSILON, step=x_tick[2]))
        if y_lim is not None and use_ylim:
            ax.set_ylim([y_lim[0], y_lim[1]])
            plt.yticks(np.arange(y_tick[0], y_tick[1]+self.EPSILON, step=y_tick[2]))
        self.use_ylim = use_ylim

    def plot_line(self, data, data_log_v=1, linewidth=1, format="", alpha=1.0, x_shift=0):
        plt.figure(self.id)
        if format:
            plt.plot((np.arange(data.shape[-1])+x_shift)*data_log_v, data, format,
                linewidth=linewidth, alpha=alpha)
        else:
            plt.plot((np.arange(data.shape[-1])+x_shift)*data_log_v, data,
                linewidth=linewidth)

    def save_fig(self, legend=[], fn_prefix="", fn_suffix=""):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        plt.figure(self.id)
        if not self.use_ylim:
            fn_suffix += "y_unlimited"
        fn = "_".join([fn_prefix, self.fn, fn_suffix]).strip("_") + ".png"
        
        if legend:
            plt.legend(legend)
        # plt.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=1.0)
        plt.savefig(os.path.join(self.output_dir, fn))
        print("fig save to {}".format(os.path.join(self.output_dir, fn)))


class PlotBarHandlder:
    _ids = itertools.count(0)
    EPSILON = 10**-5

    def __init__(self, title, xlabel, ylabel, fn, figure_ratio, figure_size=12,
        width_p=0.175, width_b=1, linewidth=1.25,
        output_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgfiles")) -> None:
        
        self.id = next(self._ids)

        self.output_dir = output_dir
        self.fn = fn
        
        plt.figure(self.id, figsize=(figure_size, figure_size*figure_ratio), dpi=160)
        if title is not None:
            plt.title(title, fontweight="bold")
        if xlabel is not None:
            plt.xlabel(xlabel)
        if ylabel is not None:
            plt.ylabel(ylabel)
        
        ax = plt.gca()
        ax.set_axisbelow(True)
        ax.set_ylim(0, 1)
        ax.yaxis.set_major_formatter(lambda x, pos: f'{x:.3f}'.rstrip('0').rstrip('.'))

        self.param_b_num = None
        self.param_p_num = 0
        self.width_p = width_p
        self.width_b = width_b
        self.linewidth = linewidth

    def plot_bar(self, p_fc: list, p_label:str, color:str,
            ):
        """
        param:
        - p_fc: list of float
            fc of different param b given a param p.
        """

        if self.param_b_num is None:
            self.param_b_num = len(p_fc)
        else:
            assert self.param_b_num == len(p_fc)

        x = np.arange(self.param_b_num) * self.width_b
        plt.bar(x + self.width_p*self.param_p_num, p_fc, self.width_p,
            edgecolor='black', linewidth=self.linewidth, color=color, label=p_label)
        plt.legend(bbox_to_anchor=(1,0.5), loc='center left')
        plt.grid(axis='y', linewidth=.75)
        self.param_p_num += 1
    
    def save_fig(self, param_b: list, fn_prefix="", fn_suffix=""):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        plt.figure(self.id)
        fn = "_".join([fn_prefix, self.fn, fn_suffix]).strip("_") + ".png"

        x = np.arange(self.param_b_num) * self.width_b
        plt.xticks(x + self.width_p*(self.param_b_num/2 - 0.5), param_b)
        plt.yticks(np.arange(0, 1.01, step=0.1))
        
        plt.savefig(os.path.join(self.output_dir, fn))
        print("fig save to {}".format(os.path.join(self.output_dir, fn)))