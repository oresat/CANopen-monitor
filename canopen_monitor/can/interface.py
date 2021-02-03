from __future__ import annotations
import psutil
import socket
import datetime as dt
from .message import Message
from pyvit.hw.socketcan import SocketCanDev


SOCK_TIMEOUT = 0.3


class Interface(SocketCanDev):
    """This is a model of a POSIX interface

    Used to manage a singular interface and any encoded messages streaming
    across it

    :param if_name: Interface name to bind to
    :type if_name: str

    :param other_thing: Some thing
    :type other_thing: bool
    """

    def __init__(self: Interface, if_name: str):
        """Interface constructor

        :param if_name: The name of the interface to bind to
        :type if_name: str
        """
        super().__init__(if_name)
        self.name = if_name
        self.last_activity = dt.datetime.now()
        self.socket.settimeout(SOCK_TIMEOUT)

    def __enter__(self: Interface) -> Interface:
        """The entry point of an `Interface` in a `with` statement

        This binds to the socket interface name specified

        :returns: Itself
        :rtype: Interface

        :Example:

        >>> with canopen_monitor.Interface('vcan0') as dev:
        >>>     print(f'Message: {dev.recv()}')
        """
        if(self.exists):
            self.start()
            return self
        else:
            return None

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

    def recv(self: Interface) -> Message:
        """A wrapper for `recv()` defined on `pyvit.hw.SocketCanDev`

        Instead of returning a `can.Frame`, it intercepts the `recv()` and
        converts it to a `canopen_monitor.Message` at the last minute.

        :return: A loaded `canopen_monitor.Message` from the interface if a
            message is recieved within the configured SOCKET_TIMEOUT (default
            is 0.3 seconds), otherwise returns None
        :rtype: Message, None
        """
        try:
            if(self.exists):
                frame = super().recv()
                return Message(frame.arb_id,
                               data=list(frame.data),
                               frame_type=frame.frame_type,
                               interface=self.name,
                               timestamp=dt.datetime.now(),
                               extended=frame.is_extended_id)
            else:
                return None
        except socket.timeout:
            return None

    @property
    def exists(self: Interface) -> bool:
        """Determines if the interface currently exists

        :returns: `True` if the interface was found, otherwise `False`
        :rtype: bool
        """
        return self.name in psutil.net_if_stats()

    @property
    def is_up(self: Interface) -> bool:
        """Determines if the interface is in the `UP` state

        :returns: `True` if in the `UP` state `False` if in the `DOWN` state
        :rtype: bool
        """
        return psutil.net_if_stats()[self.name].isup if self.exists else False

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

        This will appear as 0 for virtual can interfaces.

        :return: Baud rate
        :rtype: int
        """
        val = Interface.__get_if_data(self.name)
        return val.speed if val is not None else None

    @property
    def mtu(self: Interface) -> int:
        """MTU

        :return: MTU
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

    def __repr__(self: Interface) -> str:
        return f'({self.name}:' \
               f' {"UP" if self.is_up else "DOWN"})'
