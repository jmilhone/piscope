
def plot_discharge(axs, time, cathode_voltage, cathode_current, anode_current):
    # axs[0] is for cathode voltages
    # axs[1] is for cathode currents
    # axs[2] is for anode currents

    for cath in cathode_voltage:
        axs[0].plot(time, cathode_voltage[cath], label="{0:d}".format(cath))

    for cath in cathode_current:
        axs[1].plot(time, cathode_current[cath], label="{0:d}".format(cath))

    for anode in anode_current:
        axs[2].plot(time, anode_current[anode], label="{0:d}".format(anode))

    lg0 = axs[0].legend(frameon=False)
    # lg1 = axs[1].legend(frameon=False)
    lg2 = axs[2].legend(frameon=False)

    if lg0:
        lg0.draggable()

    # if lg1:
    #    lg1.draggable()

    if lg2:
        lg2.draggable()

    axs[0].set_xlabel("Time (s)")
    axs[1].set_xlabel("Time (s)")
    axs[2].set_xlabel("Time (s)")

    axs[0].set_ylabel("Voltage (V)")
    axs[1].set_ylabel("Cath. Cur (A)")
    axs[2].set_ylabel("Anode Cur (A)")

def plot_probes(axs, time, ne, te, vf):
    # axs[0] is for ne
    # axs[1] is for te
    # axs[2] is for vf

    for probe in ne:
        axs[0].plot(time, ne[probe], label="{0:d}".format(probe))

    for probe in te:
        axs[1].plot(time, te[probe], label="{0:d}".format(probe))

    for probe in vf:
        axs[2].plot(time, vf[probe], label="{0:d}".format(probe))

    lg0 = axs[0].legend(frameon=False)
    # lg1 = axs[1].legend(frameon=False)
    # lg2 = axs[2].legend(frameon=False)

    if lg0:
        lg0.draggable()

    # if lg1:
    #    lg1.draggable()

    # if lg2:
    #    lg2.draggable()

    axs[0].set_ylabel(r"$n_e$ (m${}^{-3}$)")
    axs[1].set_ylabel(r"$T_e$ (eV)")
    axs[2].set_ylabel(r"$V_f$ (V)")


def plot_power(ax, time, cathode_power):
    ax.plot(time, cathode_power, label="Cathodes")
    ax.set_ylabel("Power (kW)")


def plot_total_current(ax, time, cathode_current, anode_current):
    ax.plot(time, cathode_current, label="Cathodes")
    ax.plot(time, anode_current, label="Anodes")
    lg = ax.legend(frameon=False)
    if lg:
        lg.draggable()

