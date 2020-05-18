import threading
from .frame_data import FrameData
from canard.hw.socketcan import SocketCanDev
from queue import Queue


class TheMagicCanBus:
    def __init__(self, device_names=[], block=True):
        self.block = block
        self.devs = []
        self.frames = Queue()

        for name in device_names:
            self.start(name)

    def start(self, dev_name):
        dev = SocketCanDev(dev_name)
        dev.start()
        self.devs.append(dev)
        dev_listener = threading.Thread(target=self.listen,
                                        name='dev-listener-'
                                        + str(len(self.devs)),
                                        args=[dev])
        dev_listener.setDaemon(True)
        dev_listener.start()

    def stop(self):
        for dev in self.devs:
            dev.stop()

    def listen(self, dev):
        try:
            while True:
                res = dev.recv()
                self.frames.put([res, dev.ndev], block=self.block)
        except OSError as e:
            print("fatal "
                    + str(dev)
                    + ": "
                    + str(e)
                    + '\n\tKilling the thread and removing the device...')
            self.devs.remove(dev)

    def receive(self):
        res = self.frames.get(block=self.block)
        return FrameData(res[0], res[1])

    def running(self):
        return list(filter(lambda x: x.running, self.devs))
