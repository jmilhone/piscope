from __future__ import division, print_function
import MDSplus as mds
from .data import Data


def get_current_shot(tree):
    try:
        current_shot = mds.tree.Tree.getCurrent(tree)
    except mds.mdsExceptions.TreeNOCURRENT as e:
        return None
    return current_shot


def check_data_dictionary(data_dict):
    for d in data_dict:
        # data_dict[d] is a list
        for item in data_dict[d]:
            if item is not None:
                return True
    # If you make it to here, that means all items were None
    return False


def retrieve_signal(shot_number, signal_info, loc_name, signal_name, server, tree):

    try:
        con = mds.Connection(server)
        con.openTree(tree, shot_number)
        data = retrieve_data(con, signal_info, signal_name)
    except (mds.MdsIpException, mds.TreeFOPENR, mds.TdiMISS_ARG) as e:
        print("Error with shot {0:d}, loc {1}, name {2}".format(shot_number, loc_name, signal_name))
        print(e.message)
        data = None
    return loc_name, signal_name, data


def retrieve_data(connection, node_loc, name):
    try:
        if "\n" in node_loc['y']:
            ystring = node_loc['y'].splitlines()
            ystring = " ".join(ystring)
        else:
            ystring = node_loc['y']

        if "\n" in node_loc['x']:
            xstring = node_loc['x'].splitlines()
            xstring = " ".join(xstring)
        else:
            xstring = node_loc['x']
        data = connection.get(ystring).data()
        t = connection.get(xstring).data()

        return Data(name, t, data, node_loc['color'])

    except mds.MdsIpException:
        return None

    except KeyError:
        return None


