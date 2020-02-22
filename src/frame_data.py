import time
from canard.can import Frame

STALE_NODE_TIME = 60
DEAD_NODE_TIME = 600

# Expanded frame data class
class FrameData(Frame):
    def __init__(self, src, ndev):
        self.ndev = ndev
        self.last_modified = time.time()
        self.is_extended_id = src.is_extended_id
        self.dlc = src.dlc
        self.id = src.id
        self.data = src.data
        self.frame_type = src.frame_type

    def is_stale(self): return ((time.time() - self.last_modified) >= STALE_NODE_TIME)
    def is_dead(self): return ((time.time() - self.last_modified) >= DEAD_NODE_TIME)
