from __future__ import division, print_function
import MDSplus as mds
from .data import Data


def get_current_shot(tree):
    try:
        current_shot = mds.tree.Tree.getCurrent(tree)
    except mds.mdsExceptions.TreeNOCURRENT as e:
        return None
    return current_shot


def retrieve_signals(shot_number, loc_dict, loc_name, server):
    ignore_items = ['legend', 'xlabel', 'ylabel', 'xlim', 'ylim', 'color']
    print("im here")
    data = dict()
    try:
        con = mds.Connection(server)
        con.openTree("wipal", shot_number)
    except mds.MdsIpException as e:
        return None

    temp_data = list()
    for name in loc_dict:
        if name.lower() not in ignore_items:
            temp_data.append(retrieve_data(con, loc_dict[name], name))

    return loc_name, temp_data


def retrieve_signal(shot_number, signal_info, loc_name, signal_name, server, tree):

    try:
        con = mds.Connection(server)
        con.openTree(tree, shot_number)
    except mds.MdsIpException as e:
        return None
    data = retrieve_data(con, signal_info, signal_name)

    return loc_name, signal_name, data


def retrieve_all_data(shot_number, locs, server):
    #try:
    #    wipal = mds.Tree("wipal", shot_number)
    #except mds.TreeFOPENR, e:
    #    return None
    try:
        con = mds.Connection(server)
        con.openTree("wipal", shot_number)
    except mds.MdsIpException as e:
        return None

    data = {}
    for grid_position in locs:

        temp_data = []
        names = locs[grid_position].keys()
        names.sort()
        for name in names:
            if name.lower() not in ['legend', 'xlabel', 'ylabel', 'xlim', 'ylim', 'color']:
                temp_data.append(retrieve_data(con, locs[grid_position][name], name))
                #temp_data.append(retrieve_data(wipal, locs[grid_position][name], name))

        data[grid_position] = temp_data

    return data


def retrieve_data(connection, node_loc, name):
    data = None
    t = None
    # print node_loc
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
        # print xstring
        # ystring = node_loc['y'].replace("\n", "")
        # xstring = node_loc['x'].replace("\n", "")
        data = connection.get(ystring).data()
        t = connection.get(xstring).data()

        #data_obj = connection.get(node_loc)#.data()
        #data = data_obj.data()
        #t = connection.get("dim_of({0:s})".format(node_loc)).data()
    except mds.MdsIpException as e:
        pass
    except KeyError:
        data = None
        t = None

    return Data(name, t, data, node_loc['color'])

    #try:
    #    node = tree.getNode(node_loc)
    #    data = node.getData().data()
    #    t = node.dim_of().data()
    #except mds.TreeNODATA, e_nodata:
    #    pass #print name + "no data"
    #except mds.TreeNNF, e_node_not_found:
    #    pass #print name + "node not found"
    #return Data(name, t, data)


if __name__ == "__main__":
    shot_num = 30270
    locs = {'00': {u'i_cath2': u'discharge.cathodes.cathode_02.current',
                   u'i_cath1': u'discharge.cathodes.cathode_01.current',
                   u'legend': True},
            '01': {u'v_cath2': u'discharge.cathodes.cathode_02.voltage',
                   u'v_cath1': u'discharge.cathodes.cathode_01.voltage',
                   u'legend': False}}

    retrieve_all_data(shot_num, locs)
