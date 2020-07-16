import os.path
import json
import monitor


def prime_config_dir(exist_ok: bool = True):
    os.makedirs(monitor.CANMONITOR_CONFIG_DIR, exist_ok=exist_ok)


def load_config(filename: str):
    '''Load a pre-existing json config'''
    file = open(os.path.expanduser(filename))
    raw_data = file.read()
    file.close()
    return json.loads(raw_data)


def config_factory(filepath: str):
    '''Generate the default configs'''
    if(filepath == monitor.CANMONITOR_DEVICES_CONFIG):
        data = ['can0']
    elif(filepath == monitor.CANMONITOR_LAYOUT_CONFIG):
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
                            'frame_types': ['HB']
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
                    'EMCY',
                    'TIME',
                    'TPDO1',
                    'RPDO1',
                    'TPDO2',
                    'RPDO2',
                    'TPDO3',
                    'RPDO3',
                    'TPDO4',
                    'RPDO4',
                    'TSDO',
                    'RSDO',
                    'UKOWN'
                ]
            }]}
    else:
        data = {}

    file = open(os.filepath.expanduser(filepath), 'w+')
    file.write(json.dumps(data, sort_keys=True, indent=4) + '\n')
    file.close()
