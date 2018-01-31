import MDSplus as mds
import node_names


def retrieve_cathode_data(wipal_tree, n_cathodes=12, npts=100):
    cathodes = range(1, n_cathodes+1)
    current_node_paths = node_names.cathode_current_node_locations(n_cathodes=n_cathodes)
    voltage_node_paths = node_names.cathode_voltage_node_locations(n_cathodes=n_cathodes)
    power_node_paths = node_names.cathode_power_node_locations(n_cathodes=n_cathodes)

    t, cathode_current = _retrieve_data(wipal_tree, cathodes, current_node_paths, npts=npts)
    _, cathode_voltage = _retrieve_data(wipal_tree, cathodes, voltage_node_paths, npts=npts)
    _, cathode_power = _retrieve_data(wipal_tree, cathodes, power_node_paths, npts=npts)

    total_power = 0.0
    total_current = 0.0
    for cath in cathode_power:
        total_power += cathode_power[cath]
        total_current += cathode_current[cath]

    return t, cathode_current, cathode_voltage, total_power, total_current


def retrieve_anode_data(wipal_tree, n_anodes=20, npts=100):
    anodes = range(1, n_anodes+1)
    anode_node_paths = node_names.anode_current_node_locations(n_anodes=n_anodes)

    t, anode_current = _retrieve_data(wipal_tree, anodes, anode_node_paths, npts=npts)

    total_current = 0.0
    for anode in anode_current:
        total_current -= anode_current[anode]

    return t, anode_current, total_current


def retrieve_triple_probe_data(wipal_tree, n_probes=5, npts=100):
    probes = range(1, n_probes+1)
    te_node_paths = node_names.mach_triple_te_node_locations(n_probes=n_probes)
    ne_node_paths = node_names.mach_triple_ne_node_locations(n_probes=n_probes)
    vf_node_paths = node_names.mach_triple_vf_node_locations(n_probes=n_probes)

    t, te = _retrieve_data(wipal_tree, probes, te_node_paths, npts=npts)
    _, ne = _retrieve_data(wipal_tree, probes, ne_node_paths, npts=npts)
    _, vf = _retrieve_data(wipal_tree, probes, vf_node_paths, npts=npts)

    return t, ne, te, vf


def retrieve_all_data(shot_number, n_anodes=20, n_cathodes=12, n_probes=5, npts=100):
    tree = mds.Tree("wipal", shot_number)

    t, cathode_current, cathode_voltage, total_power, total_cathode_current = retrieve_cathode_data(tree, n_cathodes=n_cathodes, npts=npts)
    _, anode_current, total_anode_current = retrieve_anode_data(tree, npts=npts, n_anodes=n_anodes)
    tt, te, ne, vf = retrieve_triple_probe_data(tree, n_probes=n_probes, npts=npts)
    return t, cathode_current, cathode_voltage, anode_current, total_power, total_cathode_current, total_anode_current, tt, te, ne, vf


def _retrieve_data(tree, labels, paths, npts=100):
    data = {}
    t = None
    for lab, path in zip(labels, paths):
        try:
            node = tree.getNode(path)
            data[lab] = node.getData().data()[::npts]
            if t is None:
                t = node.dim_of().data()[::npts]
        except mds.TreeNODATA, e:
            pass
    return t, data


