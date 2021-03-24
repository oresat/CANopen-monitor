from .eds import EDS
from .utilities import FailedValidationError
from ..can import MessageType

STATE_BYTE_IDX = 0


def parse(cob_id: int, data: list, eds_config: EDS):
    """
    Parse Heartbeat message

    Arguments
    ---------
    :param data: a byte string containing the heartbeat message, byte 0 is the
    heartbeat state info.

    :return: the parsed message
    :rtype: str
    """
    states = {
        0x00: "Boot-up",
        0x04: "Stopped",
        0x05: "Operational",
        0x7F: "Pre-operational"
    }

    node_id = MessageType.cob_to_node(MessageType.HEARTBEAT, cob_id)
    if len(data) < 1 or data[STATE_BYTE_IDX] not in states:
        raise FailedValidationError(data, node_id, cob_id, __name__,
                                    "Invalid heartbeat state detected")
    return states.get(data[STATE_BYTE_IDX])
