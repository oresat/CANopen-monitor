from __future__ import annotations
from .interface import Interface
from .message import Message
import queue
import threading as t


class MagicCANBus:
    """This is a macro-manager for multiple CAN interfaces

    :param interfaces: The list of serialized Interface objects the bus is
        managing
    :type interfaces: [Interface]
    """

    def __init__(self: MagicCANBus, if_names: [str], no_block: bool = False):
        self.interfaces = list(map(lambda x: Interface(x), if_names))
        self.no_block = no_block
        self.keep_alive_list = dict()
        self.message_queue = queue.SimpleQueue()
        self.threads = []

    @property
    def statuses(self: MagicCANBus) -> [tuple]:
        """This property is simply an aggregate of all of the interfaces and
        whether or not they both exist and are in the `UP` state

        :return: a list of tuples containing the interface names and a bool
            indication an `UP/DOWN` status
        :rtype: [tuple]
        """
        return list(map(lambda x: (x.name, x.is_up), self.interfaces))

    @property
    def interface_list(self: MagicCANBus) -> [str]:
        """A list of strings representing all interfaces
        :return: a list of strings indicating the name of each interface
        :rtype: [str]
        """
        return list(map(lambda x: str(x), self.interfaces))

    def add_interface(self: MagicCANBus, interface: str) -> None:
        """This will add an interface at runtime

        :param interface: The name of the interface to add
        :type interface: string"""

        # Check if interface is already existing
        interface_names = self.interface_list
        if interface in interface_names:
            return

        new_interface = Interface(interface)
        self.interfaces.append(new_interface)
        self.threads.append(self.start_handler(new_interface))

    def remove_interface(self: MagicCANBus, interface: str) -> None:
        """This will remove an interface at runtime

        :param interface: The name of the interface to remove
        :type interface: string"""

        # Check if interface is already existing
        interface_names = self.interface_list
        if interface not in interface_names:
            return

        self.keep_alive_list[interface].clear()
        for thread in self.threads:
            if thread.name == f'canopen-monitor-{interface}':
                thread.join()
                self.threads.remove(thread)
                del self.keep_alive_list[interface]

        for existing_interface in self.interfaces:
            if str(existing_interface) == interface:
                self.interfaces.remove(existing_interface)

    def start_handler(self: MagicCANBus, iface: Interface) -> t.Thread:
        """This is a wrapper for starting a single interface listener thread
            This wrapper also creates a keep alive event for each thread which
            can be used to kill the thread.

        .. warning::

                If for any reason, the interface cannot be listened to, (either
                it doesn't exist or there are permission issues in reading from
                it), then the default behavior is to stop listening for
                messages, block wait for the interface to come back up, then
                resume. It is possible that a thread starts but no listener
                starts due to a failure to bind to the interface.

        :param iface: The interface to bind to when listening for messages
        :type iface: Interface

        :return: The new listener thread spawned
        :rtype: threading.Thread
        """
        self.keep_alive_list[iface.name] = t.Event()
        self.keep_alive_list[iface.name].set()

        tr = t.Thread(target=self.handler,
                      name=f'canopen-monitor-{iface.name}',
                      args=[iface],
                      daemon=True)
        tr.start()
        return tr

    def handler(self: MagicCANBus, iface: Interface) -> None:
        """This is a handler for listening and block-waiting for messages on
        the CAN bus

        It will operate on the condition that the Magic Can Bus is still
        active, using thread-safe events.

        :param iface: The interface to bind to when listening for messages
        :type iface: Interface
        """

        # The outer loop exists to enable interface recovery, if the interface
        #   is either deleted or goes down, the handler will try to start it
        #   again and read messages as soon as possible
        while (self.keep_alive_list[iface.name].is_set()):
            try:
                # The inner loop is the constant reading of the bus and loading
                #   of frames into a thread-safe queue. It is necessary to
                #   check `iface.is_up` in the inner loop as well, so that the
                #   handler will not block on bus reading if the MCB is trying
                #   to close all threads and destruct itself
                while (iface.is_up and iface.running and
                       self.keep_alive_list[iface.name].is_set()):
                    frame = iface.recv()
                    if (frame is not None):
                        self.message_queue.put(frame, block=True)
                iface.restart()
            except OSError:
                pass
        iface.stop()

    def __enter__(self: MagicCANBus) -> MagicCANBus:
        self.threads = list(map(lambda x: self.start_handler(x),
                                self.interfaces))
        return self

    def __exit__(self: MagicCANBus,
                 etype: str,
                 evalue: str,
                 traceback: any) -> None:
        for keep_alive in self.keep_alive_list.values():
            keep_alive.clear()
        if (self.no_block):
            print('WARNING: Skipping wait-time for threads to close'
                  ' gracefully.')
        else:
            print('Press <Ctrl + C> to quit without waiting.')
            for tr in self.threads:
                print(f'Waiting for thread {tr} to end... ', end='')
                tr.join()
                print('Done!')

    def __iter__(self: MagicCANBus) -> MagicCANBus:
        return self

    def __next__(self: MagicCANBus) -> Message:
        if (self.message_queue.empty()):
            raise StopIteration
        return self.message_queue.get(block=True)

    def __str__(self: MagicCANBus) -> str:
        # Subtract 1 since the parent thread should not be counted
        alive_threads = t.active_count() - 1
        if_list = ', '.join(list(map(lambda x: str(x), self.interfaces)))
        return f"Magic Can Bus: {if_list}," \
               f" pending messages: {self.message_queue.qsize()}" \
               f" threads: {alive_threads}"
