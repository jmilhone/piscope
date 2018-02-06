from __future__ import print_function


def cathode_current_node_locations(n_cathodes=12):
    return ["discharge.cathodes.cathode_{0:02d}.current".format(x+1) for x in range(n_cathodes)]


def cathode_power_node_locations(n_cathodes=12):
    return ["discharge.cathodes.cathode_{0:02d}.power".format(x+1) for x in range(n_cathodes)]


def cathode_voltage_node_locations(n_cathodes=12):
    return ["discharge.cathodes.cathode_{0:02d}.voltage".format(x+1) for x in range(n_cathodes)]


def anode_current_node_locations(n_anodes=20):
    return ["discharge.anodes.anode_{0:02d}.current".format(x+1) for x in range(n_anodes)]


def mach_triple_te_node_locations(n_probes=5):
    return ["kinetics.mach_triple.probe_{0:d}.tp.te".format(x+1) for x in range(n_probes)]


def mach_triple_ne_node_locations(n_probes=5):
    return ["kinetics.mach_triple.probe_{0:d}.tp.ne".format(x+1) for x in range(n_probes)]


def mach_triple_vf_node_locations(n_probes=5):
    return ["kinetics.mach_triple.probe_{0:d}.tp.vfloat".format(x+1) for x in range(n_probes)]


def mach_triple_mach_node_locations(mp, n_probes=5):
    if mp not in ["mp1", "mp2"]:
        return []
    return ["kinetics.mach_triple.probe_{0:d}.mp.{1:s}.mach".format(x+1, mp) for x in range(n_probes)]


def mach_triple_current_node_locations(mp, face, n_probes=5):
    if mp not in ["mp1", "mp2"]:
        return []
    if face not in ["A", "B"]:
        return []
    return ["kinetics.mach_triple.probe_{0:d}.mp.{1:s}.{2:s}.current".format(x+1, mp, face) for x in range(n_probes)]

def ring_anode_node_locations(n_anodes=2):
    return ["discharge.anodes.ring_{0:02d}.current".format(x+1) for x in range(n_anodes)]

def magnetron_forward_node_locations(n_mag=2):
    return ["discharge.magnetrons.magnetron_{0:d}.forward".format(x+1) for x in range(n_mag)]

def magnetron_reflected_node_locations(n_mag=2):
    return ["discharge.magnetrons.magnetron_{0:d}.reflected".format(x+1) for x in range(n_mag)]

