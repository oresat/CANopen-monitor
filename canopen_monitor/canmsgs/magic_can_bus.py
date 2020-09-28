import queue as q
import threading as t
from typing import Union
import pyvit.hw.socketcan as phs
from .. import DEBUG, TIMEOUT, canmsgs


class MagicCANBus:
    """
    A magic bus-sniffer that reads activity on the CAN bus and subsequently
    loads a thread-safe queue of CANMsg's

    Parameters
    ----------
    interfaces `[pyvit.bus.Bus]`: A list of Bus objects that the Magic CAN Bus
                                  will monitor.
    frames `queue.Queue`: The thread-safe queue of CANMsg objects to pull from.
    failed_interfaces `[str]`: A list of interface names that the Magic CAN Bus
                               failed to connect to.
    stop_listening `threading.Event`: A thread-safe event that triggers when
                                      it's time to shut down all of the bus
                                      listeners.
    block `bool`: A flag for determining whether or not the Magic CAN Bus
                  should block when checking for CAN messages.
    threads `[threading.Thread]`: A list of bus-listener worker threads.
    """

    def __init__(self,
                 interface_names: [str] = [],
                 block: bool = True,
                 stale_timeout: int = 60,
                 dead_timeout: int = 120):
        """
        Magic CAN Bus initialization.

        Arguments
        ---------
        interface_names `[str]`: A list of interfaces to try and connect to.
        block `bool`: A flag for determining whether or not the Magic CAN Bus
                      should block when checking for CAN messages.
        """
        # Bus things
        self.interfaces = []
        self.frames = q.Queue()
        self.failed_interfaces = []
        self.stale_timeout = stale_timeout
        self.dead_timeout = dead_timeout

        # Threading things
        self.stop_listening = t.Event()
        self.block = block
        self.threads = []

        # Start all of the devices specified
        for name in interface_names:
            self.start(name)

    def start(self, dev_name):
        try:
            dev = phs.SocketCanDev(dev_name)
            dev.start()
            self.interfaces.append(dev)
            dev_listener = t.Thread(target=self._listen,
                                    args=[dev])
            dev_listener.setDaemon(True)
            dev_listener.start()
            self.threads.append(dev_listener)
        except OSError:
            self.failed_interfaces.append(dev_name)

    def _stop(self, dev):
        self.interfaces.remove(dev)

    def stop_all(self) -> None:
        """
        Remove all devices from the device table
        """
        for dev in self.interfaces:
            self._stop(dev)

        self.stop_listening.set()

        if(DEBUG):
            print('waiting for '
                  + str(len(self.threads))
                  + ' bus-threads to close.')
        if(len(self.threads) > 0):
            for thread in self.threads:
                thread.join(TIMEOUT)
                if(thread.is_alive() and DEBUG):
                    print('the bus thread listener with pid ({}) took too long to close, will try again in {}s!'.format(thread.native_id, round(TIMEOUT * len(self.threads), 3)))
            if(DEBUG):
                print('all bus threads closed gracefully!')
        else:
            if(DEBUG):
                print('no child bus threads were spawned!')

    def _listen(self, dev: phs.SocketCanDev) -> None:
        try:
            while not self.stop_listening.is_set():
                self.frames.put([dev.recv(), dev.ndev], block=self.block)
        except q.Full:
            pass
        except OSError:
            self._stop(dev)

    def receive(self) -> Union[canmsgs.CANMsg, None]:
        """
        Returns the first available CANMsg retrieved from the bus if any.
        If no messages are available on the bus, None is returned
        """
        try:
            res = self.frames.get(block=self.block,
                                  timeout=TIMEOUT)
            return canmsgs.CANMsg(res[0],
                                  res[1],
                                  self.stale_timeout,
                                  self.dead_timeout)
        except q.Empty:
            return None

    def running(self) -> [str]:
        return list(filter(lambda x: x.running, self.interfaces))
