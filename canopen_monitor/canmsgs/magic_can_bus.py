import threading
import canopen_monitor
from typing import Union
from canopen_monitor.canmsgs.canmsg import CANMsg
from canard.hw.socketcan import SocketCanDev
from queue import Queue, Full, Empty


class MagicCANBus:
    def __init__(self, device_names=[], block=True):
        # Bus things
        self.devs = []
        self.frames = Queue()
        self.failed_devs = []

        # Threading things
        self.stop_listening = threading.Event()
        self.block = block
        self.threads = []

        # Start all of the devices specified
        for name in device_names:
            self.start(name)

    def start(self, dev_name):
        try:
            dev = SocketCanDev(dev_name)
            dev.start()
            self.devs.append(dev)
            dev_listener = threading.Thread(target=self._listen,
                                            args=[dev])
            dev_listener.setDaemon(True)
            dev_listener.start()
            self.threads.append(dev_listener)
        except OSError:
            self.failed_devs.append(dev_name)

    def _stop(self, dev):
        self.devs.remove(dev)

    def stop_all(self) -> None:
        """
        Remove all devices from the device table
        """
        for dev in self.devs:
            self._stop(dev)

        self.stop_listening.set()

        if(canopen_monitor.DEBUG):
            print('waiting for '
                  + str(len(self.threads))
                  + ' bus-threads to close.')
        if(len(self.threads) > 0):
            for thread in self.threads:
                thread.join(canopen_monitor.TIMEOUT)
                if(thread.is_alive() and canopen_monitor.DEBUG):
                    print('the bus thread listener with pid ({}) took too long to close, will try again in {}s!'.format(thread.native_id, round(canopen_monitor.TIMEOUT * len(self.threads), 3)))
            if(canopen_monitor.DEBUG):
                print('all bus threads closed gracefully!')
        else:
            if(canopen_monitor.DEBUG):
                print('no child bus threads were spawned!')

    def _listen(self, dev: SocketCanDev) -> None:
        try:
            while not self.stop_listening.is_set():
                self.frames.put([dev.recv(), dev.ndev], block=self.block)
        except Full:
            pass
        except OSError:
            self._stop(dev)

    def receive(self) -> Union[CANMsg, None]:
        """
        Returns the first available CANMsg retrieved from the bus if any.
        If no messages are available on the bus, None is returned
        """
        try:
            res = self.frames.get(block=self.block, timeout=canopen_monitor.TIMEOUT)
            return CANMsg(res[0], res[1])
        except Empty:
            return None

    def running(self) -> [str]:
        return list(filter(lambda x: x.running, self.devs))
