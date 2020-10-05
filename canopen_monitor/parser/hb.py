from .eds import EDS
from .utilities import FailedValidationError
from ..canmsgs import MessageType


def parse(cob_id: int, data: bytes, eds_config: EDS):
    """
    Parse Heartbeat message

    Arguments
    ---------
    @:param: data: a byte string containing the heartbeat message

    Returns
    -------
    `str`: The parsed message
    """
    states = {
        0x00: "Boot-up",
        0x04: "Stopped",
        0x05: "Operational",
        0x7F: "Pre-operational"
    }
    node_id = MessageType.cob_id_to_node_id(cob_id)
    hex_data = int(hex(data[0]), 16)
    state = states.get(hex_data)

    if state is None:
        return "INVALID STATE ({})".format(hex_data)
    else:
        if int.from_bytes(data, "big") in states:
            return state
        else:
            raise FailedValidationError(data, node_id, cob_id, __name__,
                                        "Invalid heartbeat state detected")
