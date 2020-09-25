import os.path
import json
import canopen_monitor


def generate_dirs(exist_ok: bool = True):
    os.makedirs(canopen_monitor.CONFIG_DIR, exist_ok=exist_ok)
    os.makedirs(canopen_monitor.CACHE_DIR, exist_ok=exist_ok)
    os.makedirs(canopen_monitor.EDS_DIR, exist_ok=exist_ok)


def load_config(filename: str):
    """Loads a pre-existing json file

    Returns
    -----
    """
    file = open(os.path.expanduser(filename))
    raw_data = file.read()
    file.close()
    return json.loads(raw_data)


def config_factory(filepath: str):
    '''Generate the default configs'''
    if(filepath == canopen_monitor.DEVICES_CONFIG):
        data = ['can0']
    elif(filepath == canopen_monitor.NODES_CONFIG):
        data = {0x40: "MDC"}
    elif(filepath == canopen_monitor.LAYOUT_CONFIG):
        data = {
            'type': 'grid',
            'split': 'horizontal',
            'data': [{
                'type': 'grid',
                'split': 'vertical',
                'data': [{
                            'type': 'table',
                            'capacity': 16,
                            'dead_node_timeout': 600,
                            'name': 'Hearbeats',
                            'stale_node_timeout': 60,
                            'fields': [],
                            'frame_types': ['HEARTBEAT']
                        }, {
                            'type': 'table',
                            'capacity': 16,
                            'dead_node_timeout': 600,
                            'name': 'Info',
                            'stale_node_timeout': 60,
                            'fields': [],
                            'frame_types': []
                        }]
            }, {
                'type': 'table',
                'capacity': 16,
                'dead_node_timeout': 60,
                'name': 'Misc',
                'stale_node_timeout': 600,
                'fields': [],
                'frame_types': [
                    'NMT',
                    'SYNC',
                    'TIME',
                    'EMER',
                    'PDO1_TX',
                    'PDO1_RX',
                    'PDO2_TX',
                    'PDO2_RX',
                    'PDO3_TX',
                    'PDO3_RX',
                    'PDO4_TX',
                    'PDO4_RX',
                    'SDO_TX',
                    'SDO_RX',
                    'UKNOWN'
                ]
            }]}
    else:
        data = {}

    file = open(os.path.expanduser(filepath), 'w+')
    file.write(json.dumps(data, sort_keys=True, indent=4) + '\n')
    file.close()
