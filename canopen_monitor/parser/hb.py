heartbeat_statuses = {0x00: "Initializing",
                      0x04: "Stopped",
                      0x05: "Operational",
                      0x7f: "Pre-Operational"}

def parse(data: bytes):
    return 'Heartbeat!'
