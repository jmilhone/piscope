import MDSplus as mds
import node_names
# import time
# import matplotlib.pyplot as plt


def retrieve_cathode_data(wipal_tree, n_cathodes=12, npts=100):
    cathodes = range(1, n_cathodes+1)
    current_node_paths = node_names.cathode_current_node_locations(n_cathodes=n_cathodes)
    voltage_node_paths = node_names.cathode_voltage_node_locations(n_cathodes=n_cathodes)

    t, cathode_current = _retrieve_data(wipal_tree, cathodes, current_node_paths, npts=npts)
    _, cathode_voltage = _retrieve_data(wipal_tree, cathodes, voltage_node_paths, npts=npts)

    return t, cathode_current, cathode_voltage


def retrieve_anode_data(wipal_tree, n_anodes=20, npts=100):
    anodes = range(1, n_anodes+1)
    anode_node_paths = node_names.anode_current_node_locations(n_anodes=n_anodes)

    t, anode_current = _retrieve_data(wipal_tree, anodes, anode_node_paths, npts=npts)

    return t, anode_current


def retrieve_all_data(shot_number, n_anodes=20, n_cathodes=12, npts=100):
    tree = mds.Tree("wipal", shot_number)

    t, cathode_current, cathode_voltage = retrieve_cathode_data(tree, n_cathodes=n_cathodes, npts=100)
    _, anode_current = retrieve_anode_data(tree, npts=100, n_anodes=n_anodes)

    return t, cathode_current, cathode_voltage, anode_current


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


# if __name__ == "__main__":
#     shot_number = 29374
#     wipal_tree = mds.Tree("wipal", shot_number)
#     t, cathode_current, cathode_voltage = retrieve_cathode_data(wipal_tree, npts=100)
#     _, anode_current = retrieve_anode_data(wipal_tree, npts=100)
#     keys = cathode_current.keys()

    # fig, ax = plt.subplots(3)
    # for cath in cathode_voltage:
    #     ax[0].plot(t, cathode_voltage[cath], label="{0:d}".format(cath))
    # for cath in cathode_current:
    #     ax[1].plot(t, cathode_current[cath], label="{0:d}".format(cath))
    # for anode in anode_current:
    #     ax[2].plot(t, anode_current[anode], label="{0:d}".format(anode))
    # lg0 = ax[0].legend(frameon=False)
    # lg1 = ax[1].legend(frameon=False)
    # lg2 = ax[2].legend(frameon=False)
    # if lg0:
    #     lg0.draggable()
    # if lg1:
    #     lg1.draggable()
    # if lg2:
    #     lg2.draggable()
    # plt.show()


