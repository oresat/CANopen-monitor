from __future__ import annotations
import queue as q
import threading as t
from . import CANMsg, Interface


class MagicCANBus:
    """
    A magic bus-sniffer that reads activity on the CAN bus and subsequently
    loads a thread-safe queue of CANMsg's

    Parameters
    ----------
    interfaces `[pyvit.bus.Bus]`: A list of Bus objects that the Magic CAN Bus
    will monitor.

    frames `queue.Queue`: The thread-safe queue of CANMsg objects to pull from.

    stop_listeners `threading.Event`: A thread-safe event that triggers when
    it's time to shut down all of the bus listeners.

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

        self.stale_timeout = stale_timeout
        self.dead_timeout = dead_timeout

        # Threading things
        self.stop_listening = t.Event()
        self.block = block
        self.threads = []

        # Start all of the devices specified
        for name in interface_names:
            self.start(name)

    def __iter__(self: MagicCANBus):
        self.__pos = 0
        return self

    def __next__(self: MagicCANBus) -> CANMsg:
        if(self.__pos < self.frames.qsize()):
            return self.frames.get_nowait()
        else:
            raise StopIteration()

    def start(self: MagicCANBus, if_name: str) -> None:
        iface = Interface(if_name)
        iface.start()
        self.interfaces.append(iface)

        # try:
        #     new_iface = Interface(if_name)
        #     new_iface.start()
        #     self.interfaces.append(new_iface)
        #     iface_listener = t.Thread(target=self._listen,
        #                             args=[dev])
        #     dev_listener.setDaemon(True)
        #     dev_listener.start()
        #     self.threads.append(dev_listener)
        # except OSError:
        #     self.failed_interfaces.append(dev_name)

    # def _stop(self, dev):
    #     self.interfaces.remove(dev)

    # def stop_all(self) -> None:
    #     """
    #     Remove all devices from the device table
    #     """
    #     for dev in self.interfaces:
    #         self._stop(dev)
    #
    #     self.stop_listening.set()
    #
    #     if(DEBUG):
    #         print('waiting for '
    #               + str(len(self.threads))
    #               + ' bus-threads to close.')
    #     if(len(self.threads) > 0):
    #         for thread in self.threads:
    #             thread.join(TIMEOUT)
    #             if(thread.is_alive() and DEBUG):
    #                 print('the bus thread listener with pid ({}) took too long'
    #                       ' to close, will try again in {}s!'
    #                       .format(thread.native_id,
    #                               round(TIMEOUT * len(self.threads), 3)))
    #         if(DEBUG):
    #             print('all bus threads closed gracefully!')
    #     else:
    #         if(DEBUG):
    #             print('no child bus threads were spawned!')

    def __listen(self, iface: Interface) -> None:
        try:
            while not self.stop_listening.is_set():
                self.frames.put([iface.recv(), iface.ndev], block=self.block)
        except q.Full:
            pass
        except OSError:
            self._stop(iface)

    def running(self) -> [str]:
        return list(filter(lambda x: x.running, self.interfaces))
