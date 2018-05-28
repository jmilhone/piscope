from __future__ import division, print_function
import MDSplus as mds
from .data import Data
from ..logging.piscope_logging import log, time_log
import logging
from functools import lru_cache

logger = logging.getLogger('pi-scope-logger')

@log(logger)
def get_current_shot(server, tree):
    try:
        con = mds.Connection(server)
        con.openTree(tree, 0)
        current_shot = int(con.get("$SHOT"))
        return current_shot
    except mds.mdsExceptions.TreeNOCURRENT as e:
        logger.warning('TreeNOCURRENT in get_current_shot')
        return
    except (mds.MdsIpException, mds.TreeFOPENR, mds.TdiMISS_ARG) as e:
        logger.warning('Random MDSplus error in get_current_shot')
        return
    except ValueError as e:
        logger.warning('ValueError in get_current_shot')
        return


@log(logger)
def check_data_dictionary(data_dict):
    for d in data_dict:
        # data_dict[d] is a list
        for item in data_dict[d]:
            if item is not None:
                return True
    # If you make it to here, that means all items were None
    return False


@log(logger)
def check_open_tree(shot_number, server, tree):
    try:
        con = mds.Connection(server)
        con.openTree(tree, shot_number)
        return True
    except (mds.MdsIpException, mds.TreeFOPENR, mds.TdiMISS_ARG) as e:
        logger.warning('Error opening shot %d' % shot_number)
        # print("Error with shot {0:d}".format(shot_number))
        # print(e.message)
        return False


# @log(logger)
# def retrieve_signal(shot_number, signal_info, loc_name, signal_name, server, tree):

    # try:
    #     con = mds.Connection(server)
    #     con.openTree(tree, shot_number)
    #     logger.debug("Retrieving data for %s" % signal_name)
    #     data = retrieve_data(con, signal_info, signal_name)
    # except (mds.MdsIpException, mds.TreeFOPENR, mds.TdiMISS_ARG) as e:
    #     logger.warn('Random MDSplus error in retrieve_signal')
    #     # print("Error with shot {0:d}, loc {1}, name {2}".format(shot_number, loc_name, signal_name))
    #     # print(e.message)
    #     data = None
    # return loc_name, signal_name, data


@log(logger)
def retrieve_signal(shot_number, signal_info, loc_name, signal_name, server, tree):
    xstring = signal_info['x']
    ystring = signal_info['y']
    color = signal_info['color']

    data = _retrieve_signal(shot_number, server, tree, xstring, ystring,
                           signal_name, color)

    return loc_name, signal_name, data

    # try:
    #     con = mds.Connection(server)
    #     con.openTree(tree, shot_number)
    #     logger.debug("Retrieving data for %s" % signal_name)
    #     data = retrieve_data(con, signal_info, signal_name)
    # except (mds.MdsIpException, mds.TreeFOPENR, mds.TdiMISS_ARG) as e:
    #     logger.warn('Random MDSplus error in retrieve_signal')
    #     # print("Error with shot {0:d}, loc {1}, name {2}".format(shot_number, loc_name, signal_name))
    #     # print(e.message)
    #     data = None
    # return loc_name, signal_name, data


@lru_cache(maxsize=512)
def _retrieve_signal(shot_number, server, tree, xstring, ystring, name, color):
    try:
        con = mds.Connection(server)
        con.openTree(tree, shot_number)
        logger.debug("Retrieving data for %s" % name)
        data = retrieve_data(con, xstring, ystring, name, color)
        return data

    except (mds.MdsIpException, mds.TreeFOPENR, mds.TdiMISS_ARG) as e:
        logger.warning('Random MDSplus error in retrieve_signal')
        return


@time_log(logger)
def retrieve_data(connection, xstr, ystr, name, color):
    try:
        if "\n" in ystr:
            ystring = ystr.splitlines()
            ystring = " ".join(ystring)
        else:
            ystring = ystr

        if "\n" in xstr:
            xstring = xstr.splitlines()
            xstring = " ".join(xstring)
        else:
            xstring = xstr

        data = connection.get(ystring)
        t = connection.get(xstring)

        # apparently you can get None without any errors
        if data is None or t is None:
            return None

        data = data.data()
        t = t.data()

        return Data(name, t, data, color)

    except mds.MdsIpException:
        logger.warning('MdsIPException occurred in retrieve_data for %s' % name)
        return
    except mds.TreeNODATA:
        logger.warning('TreeNODATA occurred in retrieve_data for %s' % name)
        return
    except KeyError:
        logger.warning('KeyError occured in retrieve_data for %s' % name)
        return

# @time_log(logger)
# def retrieve_data(connection, node_loc, name):
#     try:
#         if "\n" in node_loc['y']:
#             ystring = node_loc['y'].splitlines()
#             ystring = " ".join(ystring)
#         else:
#             ystring = node_loc['y']

        # if "\n" in node_loc['x']:
        #     xstring = node_loc['x'].splitlines()
        #     xstring = " ".join(xstring)

        #     xstring = node_loc['x']

        # data = connection.get(ystring)
        # t = connection.get(xstring)

        # # apparently you can get None without any errors
        # if data is None or t is None:
        #     return None

        # data = data.data()
        # t = t.data()

        # return Data(name, t, data, node_loc['color'])

    # except mds.MdsIpException:
    #     logger.warn('MdsIPException occurred in retrieve_data for %s' % name)
    #     return
    # except mds.TreeNODATA as e:
    #     logger.warn('TreeNODATA occurred in retrieve_data for %s' % name)
    #     return
    # except KeyError:
    #     logger.warn('KeyError occured in retrieve_data for %s' % name)
    #     return



