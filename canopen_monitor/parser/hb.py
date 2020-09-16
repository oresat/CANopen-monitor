"""
Parse Heartbeat message

@:param: data: a byte string containing the heartbeat message
@:returns: string describing the message
"""


def parse(data: bytes):
    states = {
        0x00: "Boot-up",
        0x04: "Stopped",
        0x05: "Operational",
        0x7F: "Pre-operational"
    }

    if int.from_bytes(data, "big") in states:
        return f"Heartbeat - {states[int.from_bytes(data, 'big')]}"
    else:
        raise ValueError("Invalid heartbeat state detected")
