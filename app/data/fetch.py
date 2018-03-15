from __future__ import print_function
import readline
import MDSplus as mds
import node_names
import numpy as np


def retrieve_cathode_data(wipal_tree, n_cathodes=12, npts=100):
    cathodes = range(1, n_cathodes+1)
    current_node_paths = node_names.cathode_current_node_locations(n_cathodes=n_cathodes)
    voltage_node_paths = node_names.cathode_voltage_node_locations(n_cathodes=n_cathodes)
    power_node_paths = node_names.cathode_power_node_locations(n_cathodes=n_cathodes)

    t, cathode_current = _retrieve_data(wipal_tree, cathodes, current_node_paths, npts=npts)
    _, cathode_voltage = _retrieve_data(wipal_tree, cathodes, voltage_node_paths, npts=npts)
    _, cathode_power = _retrieve_data(wipal_tree, cathodes, power_node_paths, npts=npts)

    try:
        total_power = wipal_tree.getNode("\\cathode_power_tot").data()[::npts]
        total_current = wipal_tree.getNode("\\cathode_current_tot").data()[::npts]
    except mds.TreeNODATA, e:
        total_power = None
        total_current = None
    except IndexError, ie:
        total_power = None
        total_current = None
    return t, cathode_current, cathode_voltage, total_power, total_current


def retrieve_anode_data(wipal_tree, n_anodes=20, npts=100):
    anodes = range(1, n_anodes+1)
    anode_node_paths = node_names.anode_current_node_locations(n_anodes=n_anodes)
    ring_anode_paths = node_names.ring_anode_node_locations(n_anodes=2)
    ring_labels = ["ring {0:d}".format(x+1) for x in range(2)]

    t, anode_current = _retrieve_data(wipal_tree, anodes, anode_node_paths, npts=npts)
    _, ring_current = _retrieve_data(wipal_tree, ring_labels, ring_anode_paths, npts=npts)

    # append ring current data to anode dictionary
    for x in ring_current:
        anode_current[x] = ring_current[x]
    try:
        total_current = wipal_tree.getNode("\\anode_current_tot").data()[::npts]*-1
    except mds.TreeNODATA, e:
        total_current = None
    except IndexError, ie:
        total_current = None

    return t, anode_current, total_current


def retrieve_triple_probe_data(wipal_tree, n_probes=5, npts=100):
    probes = range(1, n_probes+1)
    te_node_paths = node_names.mach_triple_te_node_locations(n_probes=n_probes)
    ne_node_paths = node_names.mach_triple_ne_node_locations(n_probes=n_probes)
    vf_node_paths = node_names.mach_triple_vf_node_locations(n_probes=n_probes)

    t, te = _retrieve_data(wipal_tree, probes, te_node_paths, npts=npts)
    _, ne = _retrieve_data(wipal_tree, probes, ne_node_paths, npts=npts)
    _, vf = _retrieve_data(wipal_tree, probes, vf_node_paths, npts=npts)
    # clean ne here
    for probe in ne:
        ne[probe][np.isnan(ne[probe])] = 0.0
    return t, ne, te, vf



def retrieve_discharge_data(shot_number, n_anodes=20, n_cathodes=12, n_probes=5, npts=100, n_mag=2):
    tree = mds.Tree("wipal", shot_number)
    t, cathode_current, cathode_voltage, total_power, total_cathode_current = retrieve_cathode_data(tree, n_cathodes=n_cathodes, npts=npts)
    _, anode_current, total_anode_current = retrieve_anode_data(tree, npts=npts, n_anodes=n_anodes)
    tt, te, ne, vf = retrieve_triple_probe_data(tree, n_probes=n_probes, npts=npts)
    t_mag, forward, reflected = retrieve_magnetron_data(tree, n_mag=n_mag, npts=npts)
    t_mm, ne_mm = retrieve_interferometer_data(shot_number)
    t_nn, nn = retrieve_ccg_data(shot_number)

    return t, cathode_current, cathode_voltage, anode_current, total_power, total_cathode_current, total_anode_current, tt, te, ne, vf, t_mm, ne_mm, \
            t_mag, forward, reflected, t_nn, nn

def retrieve_ccg_data(shot_number):
    try:
        proc_tree = mds.Tree("mpdx_proc", shot_number)

    except mds.TreeFOPENR, e:
        print(e)
        return None, None
    
    try:
        node = proc_tree.getNode("\\ndens_ccg1")
        t = node.dim_of().data()
        nn = node.data()
        return t, nn
    except mds.TreeNODATA, e:
        print(e)
        return None, None

def retrieve_interferometer_data(shot_number):

    try:
        proc_tree = mds.Tree("mpdx_proc", shot_number)
    except mds.TreeFOPENR, e:
        print(e)
        return None, None 

    try:
        node = proc_tree.getNode("\\dens_interf")
        t = node.dim_of().data()
        ne = node.data()
        return t, ne
    except mds.TreeNODATA, e:
        print(e)
        return None, None


def retrieve_mach_data(shot_number, n_probes=5, npts=100, thres=0.001):
    tree = mds.Tree("wipal", shot_number)
    t, mp1_mach = retrieve_mach_number(tree, "mp1", n_probes=n_probes, npts=npts)
    _, mp2_mach = retrieve_mach_number(tree, "mp2", n_probes=n_probes, npts=npts)
    #print(mp1_mach)
    #print(mp2_mach)
    _, mp1_A = retrieve_mach_current(tree, "mp1", "A", n_probes=n_probes, npts=npts)
    _, mp1_B = retrieve_mach_current(tree, "mp1", "B", n_probes=n_probes, npts=npts)
    _, mp2_A = retrieve_mach_current(tree, "mp2", "A", n_probes=n_probes, npts=npts)
    _, mp2_B = retrieve_mach_current(tree, "mp2", "B", n_probes=n_probes, npts=npts)

    for probe in mp1_mach:
        clean_mach_data(mp1_mach[probe], mp1_A[probe], mp1_B[probe], thres=thres)

    for probe in mp2_mach:
        clean_mach_data(mp2_mach[probe], mp2_A[probe], mp2_B[probe], thres=thres)

    return t, mp1_mach, mp2_mach, mp1_A, mp1_B, mp2_A, mp2_B


def clean_mach_data(mach, current1, current2, thres=0.001):
    idx = np.where(np.logical_and(current1 < thres, current2 < thres))
    mach[idx] = 0.0


def retrieve_mach_current(tree, mp, face, n_probes=5, npts=100):
    current_paths = node_names.mach_triple_current_node_locations(mp, face, n_probes=n_probes)
    labels = range(1, n_probes+1)

    if len(current_paths) > 0:
        t, data = _retrieve_data(tree, labels, current_paths, npts=npts)
        return t, data
    return {}


def retrieve_mach_number(tree, mp, n_probes=5, npts=100):
    mach_paths = node_names.mach_triple_mach_node_locations(mp, n_probes=n_probes)
    labels = range(1,  n_probes+1)

    if len(mach_paths) > 0:
        t, data = _retrieve_data(tree, labels, mach_paths, npts=npts)
        return t, data
    return {}

def retrieve_magnetron_data(wipal_tree, n_mag=2, npts=100):
    mags = range(1, n_mag+1)
    forward_paths = node_names.magnetron_forward_node_locations(n_mag=n_mag)
    reflected_paths = node_names.magnetron_reflected_node_locations(n_mag=n_mag)

    t, forward = _retrieve_data(wipal_tree, mags, forward_paths, npts=npts)
    _, reflected = _retrieve_data(wipal_tree, mags, reflected_paths, npts=npts)

    return t, forward, reflected


def retrieve_gun_data(shot_number, nguns=19, npts=100):
    wipal_tree = mds.Tree("wipal", shot_number)
    Iarc_tags = ["\\gun_{0:02d}_i_arc".format(x) for x in range(1, 20)]
    Varc_tags = ["\\gun_{0:02d}_v_arc".format(x) for x in range(1, 20)]
    Ibias_tags = ["\\gun_{0:02d}_i_bias".format(x) for x in range(1, 20)]
    Vbias_tags = ["\\gun_{0:02d}_v_bias".format(x) for x in range(1, 20)]

    labels = range(1, nguns+1)

    t, Iarc = _retrieve_data(wipal_tree, labels, Iarc_tags, npts=npts)
    _, Varc = _retrieve_data(wipal_tree, labels, Varc_tags, npts=npts)
    _, Ibias = _retrieve_data(wipal_tree, labels, Ibias_tags, npts=npts)
    _, Vbias = _retrieve_data(wipal_tree, labels, Vbias_tags, npts=npts)

    valid_guns = np.zeros(nguns)
    for bias in Iarc:
        if np.mean(Iarc[bias]) > 100:
            valid_guns[bias-1] = 1.0

    try:
        node = wipal_tree.getNode("\\guns_locs")
        locs = node.getData().data()
    except mds.TreeNODATA, e:
        pass

    total = gun_totals(wipal_tree, npts=npts)

    Iarc_tot = total['I_arc_tot']
    Ibias_tot = total['I_bias_tot']
    Parc_tot = total['P_arc_tot']
    Pbias_tot = total['P_bias_tot']

    gun_data = {'t': t, "Iarc": Iarc, "Varc": Varc, "Ibias": Ibias, "Vbias": Vbias, "locs": locs,
            "Iarc_tot": Iarc_tot, "Ibias_tot": Ibias_tot, "Parc_tot": Parc_tot, "Pbias_tot": Pbias_tot, 
            "valid_guns": valid_guns}

    return gun_data


def gun_totals(wipal_tree, npts=100):
    labels = ["I_arc_tot", "I_bias_tot", "P_arc_tot", "P_bias_tot"]
    paths = ["\\guns_" + s for s in labels]

    _, data = _retrieve_data(wipal_tree, labels, paths, npts=npts)

    return data

def retrieve_linear_hall(shot_number, magnetics_tree, binned=False):
    wipal_tree = mds.Tree("wipal", shot_number)

    try:
        node_name = "\\linear_hall{0}_bx".format(magnetics_tree)
        if binned:
            node_name += "_binned"
        bx = wipal_tree.getNode(node_name).data()*10000.0
        t = wipal_tree.getNode(node_name).dim_of().data()
    except mds.TreeNODATA, e:
        bx = None

    try:
        node_name = "\\linear_hall{0}_by".format(magnetics_tree)
        if binned:
            node_name += "_binned"
        by = wipal_tree.getNode(node_name).data()*10000.0
    except mds.TreeNODATA, e:
        by = None

    try:
        node_name = "\\linear_hall{0}_bz".format(magnetics_tree)
        if binned:
            node_name += "_binned"
        bz = wipal_tree.getNode(node_name).data()*10000.0
    except mds.TreeNODATA, e:
        bz = None

    try:
        node_name = "\\linear_hall3_locs"
        locs = wipal_tree.getNode(node_name).data()
    except mds.TreeNODATA, e:
        locs = None
    bdata = {'t': t, 'bx': bx, 'by':by, 'bz':bz, 'locs': locs}

    return bdata


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


