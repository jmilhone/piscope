from __future__ import division, print_function
from distutils.util import strtobool
from .resample import DataDisplayDownsampler
import numpy as np


def plot_all_data(axs, locs, data, downsampling=10000):
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

    for d in actual_data:
        x, y = down_sampler.downsample(d, xstart, xend)
        line, = ax.plot(x, y, label=d.name, color=d.color, lw=1)
        down_sampler.lines.append(line)

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

