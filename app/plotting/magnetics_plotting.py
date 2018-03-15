from __future__ import print_function, division
from matplotlib.pyplot import Circle
import numpy as np

def plot_magnetics(axs, data):
    t = data['t']
    locs = data['locs']
    bx = data['bx']
    by = data['by']
    bz = data['bz']

    idx = 0
    for i in range(4): # column
        for j in range(4): # row
            if i == j == 0:
                # plot locations
                x = locs[:, 0]
                z = locs[:, 2]
                axs[j][i].plot(z, x, '.', ms=1)
                axs[j][i].add_patch(Circle((0,0), 1.5, fill=None, ec='gray', alpha=0.8))
            else:
                # plot magnetics
                axs[j][i].plot(t, bx[idx, :], color="C3")
                axs[j][i].plot(t, by[idx, :], color="C2")
                axs[j][i].plot(t, bz[idx, :], color="C0")
                axs[j][i].set_ylabel("Probe {} (G)".format(idx+1)) 
                #update idx
                idx += 1

    axs[0][0].set_xlim(-1.5, 1.5)
    axs[0][0].set_ylim(-1.5, 1.5)
    axs[0][0].set_aspect(1.0)

    axs[3][0].set_xlabel("Time (s)")
    axs[3][1].set_xlabel("Time (s)")
    axs[3][2].set_xlabel("Time (s)")
    axs[3][3].set_xlabel("Time (s)")
