from canopen_monitor.parser.eds import EDS

heartbeat_statuses = {0x00: "Initializing",
                      0x02: "Stopped",
                      0x05: "Operational",
                      0x7f: "Pre-Operational"}


def parse(eds_config: EDS, data: bytes):
    data = int(str(data[0]), 16)
    status = heartbeat_statuses.get(data)

    if(status is None):
        status = "Unknown Status"
    return '{}: {}'.format(eds_config.device_info.product_name, status)
