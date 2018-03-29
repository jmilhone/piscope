from __future__ import division, print_function
from distutils.util import strtobool

def plot_all_data(axs, locs, data):
    for pos in locs:
        i, j = (int(x) for x in pos)
        plot(axs[i][j], locs[pos], data[pos])


def plot(ax, info_dict, data):
    info_keys = info_dict.keys()
    for d in data:
        if len(d.data) > 1:
            ax.plot(d.time, d.data, label=d.name)

    lg = None
    if 'legend' in info_keys and strtobool(info_dict['legend']):
        lg = ax.legend()

    if 'xlabel' in info_keys:
        ax.set_xlabel(info_dict['xlabel'])

    if 'ylabel' in info_keys:
        ax.set_ylabel(info_dict['ylabel'])

    if lg:
        lg.draggable()

