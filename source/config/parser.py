from __future__ import division, print_function
from configobj import ConfigObj


default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                  '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                  '#bcbd22', '#17becf']


def config_parser(filename):
    print(filename)
    config = ConfigObj(filename,raise_errors=True)
    config = config.dict()


    col_setup = config['setup']['col']
    col_setup = [int(x) for x in col_setup]

    # determine grid keys
    add_grid_keys(config, col_setup)

    try:
        tree = config['setup']['tree']
    except KeyError:
        config['setup']['tree'] = 'wipal'
        tree = 'wipal'

    try:
        event_name = config['setup']['event']
    except KeyError:
        config['setup']['event'] = 'raw_data_ready'

    try:
        server = config['setup']['server']
    except KeyError:
        config['setup']['server'] = 'skywalker.physics.wisc.edu'

    data_locs = get_data_locs(config)
    return config, server, tree, event_name, col_setup, data_locs


def get_data_locs(config):
    data_locs = {}
    for key in config.keys():
        if key.lower() != 'setup':
            data_locs[key] = config[key]
            #print(config[key])
            parse_data_colors(config, key)
    return data_locs


def add_grid_keys(config, column_setup):
    for col, nrow in enumerate(column_setup):
        for row in range(nrow):
            new_key = "{0:d}{1:d}".format(row, col)
            if new_key not in config:
                config[new_key] = dict()


def parse_data_colors(config, key):
    local_config = config[key]
    keys = [x for x in local_config.keys()]
    keys.sort()
    top_ignore = ['xlabel', 'ylabel', 'xlim', 'ylim', 'legend', 'noresample', 'xshare']
    j = 0
    #print(keys)
    for k in keys:
        if k not in top_ignore:
            # this is a signal
            # time to check if it has a color picked already
            if 'color' not in local_config[k].keys():
                config[key][k]['color'] = default_colors[j % 10]
                j += 1
            if isinstance(config[key][k].get('y', None), list):
                print("I found you!")
                config[key][k]['y'] = ','.join(config[key][k]['y'])
                print(config[key][k]['y'])
