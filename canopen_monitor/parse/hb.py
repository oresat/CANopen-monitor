from .eds import EDS
from .utilities import FailedValidationError
from ..can import MessageType


def parse(cob_id: int, data: list, eds_config: EDS):
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
    node_id = MessageType.cob_to_node(MessageType.HEARTBEAT, cob_id)
    if len(data) < 1 or data[0] not in states:
        raise FailedValidationError(data, node_id, cob_id, __name__,
                                    "Invalid heartbeat state detected")
    return states.get(data[0])
