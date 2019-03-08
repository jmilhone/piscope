from __future__ import division, print_function
import MDSplus as mds
from .data import Data
from ..logging.piscope_logging import log, time_log
import logging
from functools import lru_cache
import concurrent.futures

logger = logging.getLogger('pi-scope-logger')

ignore_items = ['legend', 'xlabel', 'ylabel', 'xlim', 'ylim', 'color', 'noresample', 'xshare']


def retrieve_all_data(server, tree, shot_number, config, progress_signal=None):
    signals_to_grab = []
    data = dict()

    # Prep the data dictionary with Nones and grab all of the names of signals
    for subplot_name, subplot in config.items():
        data[subplot_name] = list()
        for signal_name in subplot:
            if signal_name not in ignore_items:
                signals_to_grab.append((subplot_name, signal_name))

    n_items = len(signals_to_grab)
    n = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_signal = {executor.submit(retrieve_signal, shot_number, config[x][y], x, y, server, tree): (x, y)
                            for (x, y) in signals_to_grab}

        for future in concurrent.futures.as_completed(future_to_signal):
            subplot, name = future_to_signal[future]
            data[subplot].append(future.result())
            n += 1
            if progress_signal:
                progress_signal.emit(int(n / n_items * 100.0))

    return data


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
            if item:  # Class Data is now Truthy
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
        return False


@log(logger)
def retrieve_signal(shot_number, signal_info, loc_name, signal_name, server, tree):
    xstring = signal_info['x']
    ystring = signal_info['y']
    color = signal_info['color']
    if isinstance(ystring, list):
        ystring = ','.join(ystring)
    #print(type(shot_number), type(server), type(tree), type(xstring), type(ystring), type(signal_name), type(color), ystring)
    data = _retrieve_signal(shot_number, server, tree, xstring, ystring,
                            signal_name, color)
    return data
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


def empty_lru_cache():
    size_before_empty = _retrieve_signal.cache_info().currsize
    _retrieve_signal.cache_clear()
    logger.debug("Cache had %d items before clearing" % size_before_empty)


def log_lru_cache():
    cache_info = _retrieve_signal.cache_info()
    hits = cache_info.hits
    misses = cache_info.misses
    maxsize = cache_info.maxsize
    currsize = cache_info.currsize

    logger.debug(
        "Cache has %d hits, %d misses with %d items out of the maximum %d items" % (hits, misses, currsize, maxsize)
    )


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
        print(ystring)
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
    except mds.TreeNNF:
        logger.warning('TreeNNF occurred in retrieve_data for %s' % name)
        return 
    except KeyError:
        logger.warning('KeyError occured in retrieve_data for %s' % name)
        return
