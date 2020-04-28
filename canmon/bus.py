from canard.hw import socketcan

class Bus(socketcan.SocketCanDev):
    def __init__(self, dev_name, timeout=0.01, dead_time=3):
        super().__init__(dev_name)
        self.socket.settimeout(timeout)
        self.dead_count = 0
        self.dead_time = dead_time

    def incr(self): self.dead_count += 1
    def reset(self): self.dead_count = 0
    def is_dead(self): return (self.dead_count >= self.dead_time)
    def __str__(self): return str(self.ndev)
