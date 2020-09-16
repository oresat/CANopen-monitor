import os
import argparse
import canopen_monitor as cm
import canopen_monitor.utilities as utils
import canopen_monitor.parser.eds as eds
from canopen_monitor.monitor_app import MonitorApp
from json.decoder import JSONDecodeError


def main():
    # Setup program arguments and options
    parser = argparse.ArgumentParser(prog=cm.APP_NAME,
                                     description=cm.APP_DESCRIPTION,
                                     allow_abbrev=False)
    parser.add_argument('-v', '--verbose',
                        dest='debug',
                        action='store_true',
                        default=False,
                        help='enable additional debug info')
    parser.add_argument('-d', '--devices',
                        dest='devices',
                        type=str,
                        nargs=1,
                        default="",
                        help='specify additional busses to listen on')
    args = parser.parse_args()

    # Set important app-runtime flags
    cm.DEBUG = args.debug

    # Guarentee the config directory exists
    utils.generate_dirs()

    # Attempt to load devices config from file (path defined in ./common.py)
    try:
        dev_names = utils.load_config(cm.DEVICES_CONFIG)
    # If not found generate a new config file from the config factory
    except FileNotFoundError:
        utils.config_factory(cm.DEVICES_CONFIG)
        dev_names = utils.load_config(cm.DEVICES_CONFIG)
    # If the config is malformed stop the program
    #   and ask the user to fix the configs or destroy them
    except JSONDecodeError:
        raise JSONDecodeError('fatal: malformed config file: '
                              + cm.DEVICES_CONFIG
                              + "\n\tPlease either fix the given config or \
                            destroy it so that Can Monitor can regenerate it!")

    # Append the command-line specified devices to the config specified devices
    if(len(args.devices) > 0):
        dev_names += args.devices[0].split(' ')

    # Attemt to open tables config from file (path defined in ./common.py)
    try:
        table_schema = utils.load_config(cm.LAYOUT_CONFIG)
    # If not found generate a new config file from the config factory
    except FileNotFoundError:
        utils.config_factory(cm.LAYOUT_CONFIG)
        table_schema = utils.load_config(cm.LAYOUT_CONFIG)
    # If the config is malformed stop the program
    #   and ask the user to fix the configs or destroy them
    except JSONDecodeError:
        raise JSONDecodeError('fatal: malformed config file: '
                              + cm.LAYOUT_CONFIG
                              + "\n\tPlease either fix the given config or \
                            destroy it so that Can Monitor can regenerate it!")

    # Fetch all of the EDS files that exist
    eds_configs = {}
    for file in os.listdir(cm.EDS_DIR):
        file = cm.EDS_DIR + file
        eds_config = eds.load_eds_file(file)
        node_id = eds_config[2101].default_value

        if(cm.DEBUG):
            print('Loaded config for {}({}) witn {} registered subindicies!'
                  .format(eds_config.device_info.product_name,
                          node_id,
                          len(eds_config)))
        eds_configs[node_id] = eds_config

    # Attempt to load devices config from file (path defined in ./common.py)
    try:
        node_names = utils.load_config(cm.NODES_CONFIG)
    # If not found generate a new config file from the config factory
    except FileNotFoundError:
        utils.config_factory(cm.NODES_CONFIG)
        node_names = utils.load_config(cm.NODES_CONFIG)
    # If the config is malformed stop the program
    #   and ask the user to fix the configs or destroy them
    except JSONDecodeError:
        raise JSONDecodeError('fatal: malformed config file: '
                              + cm.NODES_CONFIG
                              + "\n\tPlease either fix the given config or \
                            destroy it so that Can Monitor can regenerate it!")

    for node_id, new_name in node_names.items():
        eds_config = eds_configs.get(node_id)
        if(eds_config is None):
            if(cm.DEBUG):
                print('Tried to override Node ID: {} but no EDS config was \
                       registered with that ID! Skipping!'.format(node_id))
        else:
            if(cm.DEBUG):
                print('Modifying {} to have product name: {}'
                      .format(eds_config, new_name))
            eds_config.device_info.product_name = new_name

    # Create the app
    canmonitor = MonitorApp(dev_names, table_schema, eds_configs)

    # Attempt to start the application
    try:
        canmonitor.start()
    except KeyboardInterrupt:
        print('Stopping {}...'.format(cm.APP_NAME))
    finally:
        # Ensure that the application is properly stopped
        #   and that all of its threads are gracefully closed out
        canmonitor.stop()
        print('Goodbye!')


if __name__ == "__main__":
    main()
