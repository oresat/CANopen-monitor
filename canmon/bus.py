import threading
from .frame_data import FrameData
from canard.hw.socketcan import SocketCanDev
from queue import Queue, Full, Empty


class TheMagicCanBus:
    def __init__(self, device_names=[], block=True, timeout=0.1):
        self.block = block
        self.timeout = timeout
        self.devs = []
        self.frames = Queue()
        self.mutex = threading.Condition()
        self.kill_threads = False

        for name in device_names:
            self.start(name)

    def start(self, dev_name):
        dev = SocketCanDev(dev_name)
        try:
            dev.start()
        except OSError:
            return
        self.devs.append(dev)
        dev_listener = threading.Thread(target=self.listen,
                                        name='dev-listener-'
                                        + str(len(self.devs)),
                                        args=[dev])
        dev_listener.setDaemon(True)
        dev_listener.start()

    def stop(self, dev):
        self.devs.remove(dev)

    def stop_all(self):
        self.mutex.acquire()
        # Remove all devices from the device table
        for dev in self.devs:
            self.stop(dev)

        # Alert all children to kill themselves
        self.kill_threads = True
        self.mutex.notifyAll()
        self.mutex.release()

    def listen(self, dev):
        try:
            while True:
                res = dev.recv()
                self.frames.put([res, dev.ndev], block=self.block)

                # Check if the thread needs to end
                self.mutex.acquire()
                self.mutex.wait_for(lambda: self.kill_threads, timeout=self.timeout)
                if(self.kill_threads):
                    break
                self.mutex.release()
        except Full:
            pass
        except OSError:
            self.stop(dev)

    def receive(self):
        try:
            res = self.frames.get(block=self.block, timeout=self.timeout)
            return FrameData(res[0], res[1])
        except Empty:
            return None

    def running(self):
        return list(filter(lambda x: x.running, self.devs))
