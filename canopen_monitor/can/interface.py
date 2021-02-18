from __future__ import annotations
import psutil
import socket
import datetime as dt
from .message import Message
from pyvit.hw.socketcan import SocketCanDev


_SOCK_TIMEOUT = 0.1
_STALE_INTERFACE = dt.timedelta(minutes=1)


class Interface(SocketCanDev):
    """This is a model of a POSIX interface

    Used to manage a singular interface and any encoded messages streaming
    across it

    :param name: Name of the interface bound to
    :type name: str

    :param last_activity: Timestamp of the last activity on the interface
    :type last_activity: datetime.datetime
    """

    def __init__(self: Interface, if_name: str):
        """Interface constructor

        :param if_name: The name of the interface to bind to
        :type if_name: str
        """
        super().__init__(if_name)
        self.name = if_name
        self.last_activity = dt.datetime.now()
        self.socket.settimeout(_SOCK_TIMEOUT)
        self.listening = False

    def __enter__(self: Interface) -> Interface:
        """The entry point of an `Interface` in a `with` statement

        This binds to the socket interface name specified.

        .. warning::
            This block-waits until the provided interface comes up before
            binding to the socket.

        :returns: Itself
        :rtype: Interface

        :Example:

        >>> with canopen_monitor.Interface('vcan0') as dev:
        >>>     print(f'Message: {dev.recv()}')
        """
        self.start()
        return self

    def __exit__(self: Interface, etype, evalue, traceback) -> None:
        """The exit point of an `Interface` in a `with` statement

        This closes the socket previously bound to

        :param etype: The type of event
        :type etype: str

        :param evalue: The event
        :type evalue: str

        :param traceback: The traceback of the previously exited block
        :type traceback: TracebackException
        """
        self.stop()

    def start(self: Interface, block_wait: bool = True) -> None:
        """A wrapper for `pyvit.hw.SocketCanDev.start()`

        If block-waiting is enabled, then instead of imediately binding to the
        interface, it waits for the state to change to `UP` first before
        binding.

        :param block_wait: Enables block-waiting
        :type block_wait: bool
        """
        while(block_wait and not self.is_up):
            pass
        super().start()
        self.listening = True

    def stop(self: Interface) -> None:
        """A wrapper for `pyvit.hw.SocketCanDev.stop()`
        """
        super().stop()
        self.listening = False

    def restart(self: Interface) -> None:
        """A macro-fuction for restarting the interface connection

        This is the same as doing:

        >>> iface.stop()
        >>> iface.start()
        """
        self.stop()
        self.start()

    def recv(self: Interface) -> Message:
        """A wrapper for `pyvit.hw.SocketCanDev.recv()`

        Instead of returning a `can.Frame`, it intercepts the `recv()` and
        converts it to a `canopen_monitor.Message` at the last minute.

        :return: A loaded `canopen_monitor.Message` from the interface if a
            message is recieved within the configured SOCKET_TIMEOUT (default
            is 0.3 seconds), otherwise returns None
        :rtype: Message, None
        """
        try:
            frame = super().recv()
            self.last_activity = dt.datetime.now()
            return Message(frame.arb_id,
                           data=list(frame.data),
                           frame_type=frame.frame_type,
                           interface=self.name,
                           timestamp=dt.datetime.now(),
                           extended=frame.is_extended_id)
        except OSError:
            return None
        except socket.timeout:
            return None

    @property
    def is_up(self: Interface) -> bool:
        """Determines if the interface is in the `UP` state

        :returns: `True` if in the `UP` state `False` if in the `DOWN` state
        :rtype: bool
        """
        if_dev = psutil.net_if_stats().get(self.name)
        if(if_dev is not None):
            return if_dev.isup and self.age < _STALE_INTERFACE
        return False

    @property
    def duplex(self: Interface) -> int:
        """Determines the duplex, if there is any

        :returns: Duplex value
        :rtype: int
        """
        val = Interface.__get_if_data(self.name)
        return val.duplex if val is not None else None

    @property
    def speed(self: Interface) -> int:
        """Determines the Baud Rate of the bus, if any

        .. warning::

            This will appear as `0` for virtual can interfaces.

        :return: Baud rate
        :rtype: int
        """
        val = Interface.__get_if_data(self.name)
        return val.speed if val is not None else None

    @property
    def mtu(self: Interface) -> int:
        """Maximum Transmission Unit

        :return: Maximum size of a packet
        :rtype: int
        """
        val = Interface.__get_if_data(self.name)
        return val.mtu if val is not None else None

    @property
    def age(self: Interface) -> dt.timedelta:
        """Deterimes the age of the message, since it was received

        :return: Age of the message
        :rtype: datetime.timedelta
        """
        return dt.datetime.now() - self.last_activity

    def __str__(self: Interface) -> str:
        return self.name
