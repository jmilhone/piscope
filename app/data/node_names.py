

def cathode_current_node_locations(n_cathodes=12):
    return ["discharge.cathodes.cathode_{0:02d}.current".format(x+1) for x in range(n_cathodes)]


def cathode_voltage_node_locations(n_cathodes=12):
    return ["discharge.cathodes.cathode_{0:02d}.voltage".format(x+1) for x in range(n_cathodes)]


def anode_current_node_locations(n_anodes=20):
    return ["discharge.anodes.anode_{0:02d}.current".format(x+1) for x in range(n_anodes)]
