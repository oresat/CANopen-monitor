from __future__ import annotations
import psutil
import datetime
from pyvit.hw.socketcan import SocketCanDev


class Interface(SocketCanDev):
    """
    A representation of a POSIX interface
    """

    def __init__(self: Interface, if_name: str):
        super().__init__(if_name)
        self.name = if_name
        self.last_activity = datetime.datetime.now()

    @property
    def is_up(self: Interface) -> bool:
        val = Interface.__get_if_data(self.name)
        return val.isup if val is not None else None

    @property
    def duplex(self: Interface) -> int:
        val = Interface.__get_if_data(self.name)
        return val.duplex if val is not None else None

    @property
    def speed(self: Interface) -> int:
        val = Interface.__get_if_data(self.name)
        return val.speed if val is not None else None

    @property
    def mtu(self: Interface) -> int:
        val = Interface.__get_if_data(self.name)
        return val.mtu if val is not None else None

    @property
    def age(self: Interface) -> datetime.timedelta:
        return datetime.datetime.now() - self.last_activity

    @staticmethod
    def __get_if_data(if_name: str) -> dict:
        return psutil.net_if_stats().get(if_name)

    def __repr__(self: Interface):
        return f'<{self.name}: {"UP" if self.is_up else "DOWN"},' \
               f' age: {self.age},' \
               f' duplex: {self.duplex},' \
               f' speed: {self.speed},' \
               f' mtu: {self.mtu}>'
