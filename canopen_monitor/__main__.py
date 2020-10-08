import os
import argparse
import canopen_monitor as cm
import canopen_monitor.utilities as utils
import canopen_monitor.parser.eds as eds
from canopen_monitor.monitor_app import MonitorApp


def ensure_config_load(filepath: str) -> dict:
    # Attempt to load config from file
    try:
        config = utils.load_config(filepath)
    # If it doesn't exist, call the config factory to generate it, then load it
    except FileNotFoundError:
        utils.config_factory(filepath)
        config = utils.load_config(filepath)
    finally:
        return config


def load_eds_configs(eds_path: str) -> dict:
    configs = {}
    for file in os.listdir(cm.EDS_DIR):
        file = cm.EDS_DIR + file
        eds_config = eds.load_eds_file(file)
        node_id = eds_config[2101].default_value

        if(cm.DEBUG):
            print('Loaded config for {}({}) witn {} registered subindicies!'
                  .format(eds_config.device_info.product_name,
                          node_id,
                          len(eds_config)))
        configs[node_id] = eds_config
    return configs


def overwrite_node_names(node_names: dict, eds_configs: dict):
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
    parser.add_argument('-i', '--interfaces',
                        dest='interfaces',
                        type=str,
                        nargs=1,
                        default="",
                        help='specify additional busses to listen on')
    args = parser.parse_args()

    # Set important app-runtime flags
    cm.DEBUG = args.debug

    # Guarentee the config directory exists
    utils.generate_dirs()

    # Fetch the devices configurations
    devices_cfg = ensure_config_load(cm.DEVICES_CONFIG)
    dev_names = devices_cfg['devices']
    timeouts = (devices_cfg['stale_timeout'], devices_cfg['dead_timeout'])

    # If any interfaces are specified by command line, add them to the list
    if(len(args.interfaces) > 0):
        dev_names += args.interfaces[0].split(' ')

    # Fetch the table schemas
    table_schema = ensure_config_load(cm.LAYOUT_CONFIG)

    # Fetch all of the EDS files that exist
    eds_configs = load_eds_configs(cm.EDS_DIR)

    # Fetch all of the node-name overrides
    node_names = ensure_config_load(cm.NODES_CONFIG)

    # Overwrite the node names
    overwrite_node_names(node_names, eds_configs)

    # Create the app
    canmonitor = MonitorApp(dev_names, timeouts, table_schema, eds_configs)

    try:
        # Start the application
        canmonitor.start()
    except KeyboardInterrupt:
        # Stop the application on Ctrl+C input
        print('Stopping {}...'.format(cm.APP_NAME))
    finally:
        # Ensure that the application is properly stopped
        #   and that all of its threads are gracefully closed out
        canmonitor.stop()
        print('Goodbye!')


if __name__ == "__main__":
    main()
