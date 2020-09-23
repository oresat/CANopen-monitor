#!/usr/bin/env python3
import os
import canopen_monitor as cm
import canopen_monitor.parser as p
import canopen_monitor.canmsgs as cmc

if __name__ == '__main__':
    interfaces = [
        'vcan0',
        'vcan1',
        'vcan2'
    ]

    # Fetch all of the EDS files that exist
    eds_configs = {}
    for file in os.listdir(cm.EDS_DIR):
        file = cm.EDS_DIR + file
        eds_config = p.load_eds_file(file)
        node_id = eds_config[2101].default_value

        print('Loaded config for {}({}) with {} registered subindicies!'
              .format(eds_config.device_info.product_name,
                      node_id,
                      len(eds_config)))
        eds_configs[node_id] = eds_config

    bus = cmc.MagicCANBus(interfaces)
    table = cmc.CANMsgTable(name='Some Random Table', capacity=57)
    parser = p.CANOpenParser(eds_configs)

    print('Magic CAN Bus: {}'.format(bus))
    for k, v in bus.__dict__.items():
        print('\t{}: {}'.format(k, v))

    while True:
        frame = bus.receive()

        if(frame is not None):
            table.add(frame)

        print('{}'.format(table.name))
        for node_id, msg in table.message_table.items():
            print('Message from Node {}: {}'.format(hex(node_id), msg))
