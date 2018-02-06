from __future__ import print_function
import numpy as np

def plot_mach_number(axs, time, mp1_mach, mp2_mach):
    i = min(len(axs), len(mp1_mach), len(mp2_mach))
    mp1_keys = np.array(mp1_mach.keys())
    mp2_keys = np.array(mp2_mach.keys())

    ind_sort = np.argsort(mp1_keys)
    mp1_keys = mp1_keys[ind_sort]
    mp2_keys = mp2_keys[ind_sort]
    for j, mp1, mp2 in zip(range(i), mp1_keys, mp2_keys):
        axs[j].plot(time, mp1_mach[mp1], label="1")
        axs[j].plot(time, mp2_mach[mp2], label="2")
    lg = axs[0].legend(frameon=False)

    if lg:
        lg.draggable()
    axs[-1].set_ylabel("Time (s)")
    for ax in axs:
        ax.set_xlabel("Mach #")

def plot_currents(axs, time, faceA, faceB):
    i = min(len(axs), len(faceA), len(faceB))

    A_keys = np.array(faceA.keys())
    B_keys = np.array(faceB.keys())

    ind_sort = np.argsort(A_keys)
    A_keys = A_keys[ind_sort]
    B_keys = B_keys[ind_sort]

    for j, a, b in zip(range(i), A_keys, B_keys):
        axs[j].plot(time, faceA[a]*1000, label="A")
        axs[j].plot(time, faceB[b]*1000, label="B")

    lg = axs[0].legend(frameon=False)
    if lg:
        lg.draggable()

    for ax in axs:
        ax.set_ylabel("mA")
    axs[-1].set_xlabel("Time (s)")
