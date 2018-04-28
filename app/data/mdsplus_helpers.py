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

# def retrieve_signals(shot_number, loc_dict, loc_name, server):
#     ignore_items = ['legend', 'xlabel', 'ylabel', 'xlim', 'ylim', 'color']
#     print("im here")
#     data = dict()
#     try:
#         con = mds.Connection(server)
#         con.openTree("wipal", shot_number)
#     except mds.MdsIpException as e:
#         return None

    # temp_data = list()
    # for name in loc_dict:
    #     if name.lower() not in ignore_items:
    #         temp_data.append(retrieve_data(con, loc_dict[name], name))

    # return loc_name, temp_data


def retrieve_signal(shot_number, signal_info, loc_name, signal_name, server, tree):

    try:
        con = mds.Connection(server)
        con.openTree(tree, shot_number)
    except mds.MdsIpException as e:
        return None, None, None
    data = retrieve_data(con, signal_info, signal_name)

    return loc_name, signal_name, data


# def retrieve_all_data(shot_number, locs, server):
#     #try:
#     #    wipal = mds.Tree("wipal", shot_number)
#     #except mds.TreeFOPENR, e:
#     #    return None
#     try:
#         con = mds.Connection(server)
#         con.openTree("wipal", shot_number)
#     except mds.MdsIpException as e:
#         return None

    # data = {}
    # for grid_position in locs:

        # temp_data = []
        # names = locs[grid_position].keys()
        # names.sort()
        # for name in names:
        #     if name.lower() not in ['legend', 'xlabel', 'ylabel', 'xlim', 'ylim', 'color']:
        #         temp_data.append(retrieve_data(con, locs[grid_position][name], name))
        #         #temp_data.append(retrieve_data(wipal, locs[grid_position][name], name))

        # data[grid_position] = temp_data

    # return data


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


