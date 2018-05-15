from __future__ import division, print_function
from distutils.util import strtobool
from .resample import DataDisplayDownsampler
import numpy as np
from ..gui.helpers import global_lcm
import matplotlib.pyplot as plt


def plot_all_data(axs, locs, data, downsampling=10000):
    print('entered plot all data')
    down_samplers = []
    for idx, pos in enumerate(locs):
        i, j = (int(x) for x in pos)
        down_samplers += [plot(axs[j][i], locs[pos], data[pos], downsampling=downsampling)]

    return down_samplers


def plot(ax, info_dict, data, downsampling=10000):
    if data is None:
        return
    info_keys = info_dict.keys()

    actual_data = []
    xstart = np.inf
    xend = -np.inf
    for d in data:
        #if len(d.data) > 1:
        if d is not None:
            actual_data += [d]

            # prep xstart and xend
            if d.time[0] < xstart:
                xstart = d.time[0]

            if d.time[-1] > xend:
                xend = d.time[-1]
    # Only include signals with data, no empty arrays
    down_sampler = DataDisplayDownsampler(actual_data, xend - xstart, ax, max_points=downsampling)

    try:
        noresample = info_dict['noresample']
    except KeyError:
        noresample = False

    for d in actual_data:

        if not noresample:
            x, y = down_sampler.downsample(d, xstart, xend)
            line, = ax.plot(x, y, label=d.name, color=d.color, lw=1)
            down_sampler.lines.append(line)
        else:
            print(d.name, "not resampling!")
            x, y = d.time, d.data
            line, = ax.plot(x, y, label=d.name, color=d.color, lw=1)

    lg = None
    if 'legend' in info_keys and strtobool(info_dict['legend']):
        lg = ax.legend()

    if 'xlabel' in info_keys:
        ax.set_xlabel(info_dict['xlabel'])

    if 'ylabel' in info_keys:
        ax.set_ylabel(info_dict['ylabel'])

    if lg:
        lg.draggable()

    if 'xlim' in info_keys:
        xlim = info_dict['xlim']
        xlim = [float(x) for x in xlim]
        ax.set_xlim(xlim)

    if 'ylim' in info_keys:
        ylim = info_dict['ylim']
        ylim = [float(y) for y in ylim]
        ax.set_ylim(ylim)

    if len(down_sampler.lines) > 0:
        ax.set_autoscale_on(False)
        ax.callbacks.connect('xlim_changed', down_sampler.update)

    return down_sampler


def create_figure(column_setup):
    figure = plt.figure(0)
    axs = []
    cols = [x for x in column_setup if x > 0]
    lcm = global_lcm(cols)
    ncols = len(cols)
    for idx, item in enumerate(cols):
        factor = lcm // item
        axes = []
        for j in range(item):
            ax = plt.subplot2grid((lcm, ncols), (factor * j, idx), rowspan=factor)
            axes.append(ax)
        axs.append(axes)

    return figure, axs

