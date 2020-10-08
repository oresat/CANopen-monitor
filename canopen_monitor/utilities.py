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
        data = {
            'devices': ['can0'],
            'stale_timeout': 60,
            'dead_timeout': 120
        }
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
                            'type': 'heartbeat_table',
                            'capacity': None,
                            'name': 'Hearbeats',
                            'fields': [],
                            'frame_types': ['HEARTBEAT']
                        }, {
                            'type': 'info_table',
                            'capacity': None,
                            'name': 'Info',
                            'fields': [],
                            'frame_types': []
                        }]
            }, {
                'type': 'misc_table',
                'capacity': None,
                'name': 'Misc',
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
