from __future__ import print_function, division
import numpy as np

def tableau20_colors():
    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                 (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                 (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                 (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                 (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)

    return tableau20

colors = tableau20_colors()


def plot_Iarc(ax, time, I):
    for arc in I:
        ax.plot(time, I[arc], color=colors[arc-1], label=str(arc))
    lg = ax.legend(frameon=False)
    if lg:
        lg.draggable()

    ax.set_ylabel("Arc Current (A)")

def plot_Varc(ax, time, V):
    for arc in V:
        ax.plot(time, V[arc], color=colors[arc-1], label=str(arc))

    ax.set_ylabel("Arc Voltage (V)")

def plot_Ibias(ax, time, I):
    for bias in I:
        ax.plot(time, I[bias], color=colors[bias-1], label=str(bias))
    lg = ax.legend(frameon=False)
    if lg:
        lg.draggable()

    ax.set_ylabel("Bias Current (A)")

def plot_Vbias(ax, time, V):
    for bias in V:
        ax.plot(time, V[bias], color=colors[bias-1], label=str(bias))
    ax.set_ylabel("Bias Voltage (V)")


def plot_total_current(ax, time, bias, arc):
    ax.plot(time, bias, label="I bias total")
    ax.plot(time, arc, label="I arc total")
    lg = ax.legend(frameon=False)
    if lg:
        lg.draggable()
    
    ax.set_ylabel("Current (A)")

def plot_total_power(ax, time, bias, arc):
    ax.plot(time, bias/1000.0, label="P bias total")
    ax.plot(time, arc/1000.0, label="P arc total")
    lg = ax.legend(frameon=False)
    if lg:
        lg.draggable()

    ax.set_ylabel("Power (kW)")


def plot_locs(ax, locs, valid):
    rvals = locs[:, 0]
    theta_vals = locs[:, 1]

    y = rvals * np.cos(theta_vals)
    x = rvals * np.sin(theta_vals)

    #ax.set_aspect('equal')

    ax.plot(x, y, 'ok')
    for idx, v in enumerate(valid):
        if v:
            ax.plot(x[idx], y[idx], 'o', color=colors[idx])
