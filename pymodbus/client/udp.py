"""Modbus client async UDP communication."""
import asyncio
import functools
import logging
import socket
import typing

from pymodbus.client.base import ModbusBaseClient, ModbusClientProtocol
from pymodbus.constants import Defaults
from pymodbus.exceptions import ConnectionException
from pymodbus.framer import ModbusFramer
from pymodbus.framer.socket_framer import ModbusSocketFramer


_logger = logging.getLogger(__name__)

DGRAM_TYPE = socket.SOCK_DGRAM


class AsyncModbusUdpClient(ModbusBaseClient):
    """**AsyncModbusUdpClient**.

    :param host: Host IP address or host name
    :param port: (optional) Port used for communication.
    :param framer: (optional) Framer class.
    :param source_address: (optional) source address of client,
    :param kwargs: (optional) Experimental parameters

    Example::

        from pymodbus.client import AsyncModbusUdpClient

        async def run():
            client = AsyncModbusUdpClient("localhost")

            await client.connect()
            ...
            await client.close()
    """

    def __init__(
        self,
        host: str,
        port: int = Defaults.UdpPort,
        framer: ModbusFramer = ModbusSocketFramer,
        source_address: typing.Tuple[str, int] = None,
        **kwargs: any,
    ) -> None:
        """Initialize Asyncio Modbus UDP Client."""
        self.protocol = None
        super().__init__(framer=framer, **kwargs)
        self.params.host = host
        self.params.port = port
        self.params.source_address = source_address

        self.loop = asyncio.get_event_loop()
        self.connected = False
        self.delay_ms = self.params.reconnect_delay
        self.reset_delay()

    async def connect(self):  # pylint: disable=invalid-overridden-method
        """Start reconnecting asynchronous udp client.

        :meta private:
        """
        # force reconnect if required:
        host = self.params.host
        await self.close()
        self.params.host = host

        # get current loop, if there are no loop a RuntimeError will be raised
        self.loop = asyncio.get_running_loop()

        txt = f"Connecting to {self.params.host}:{self.params.port}."
        _logger.debug(txt)

        # getaddrinfo returns a list of tuples
        # - [(family, type, proto, canonname, sockaddr),]
        # We want sockaddr which is a (ip, port) tuple
        # udp needs ip addresses, not hostnames
        # TBD: addrinfo = await self.loop.getaddrinfo(self.params.host, self.params.port, type=DGRAM_TYPE)
        # TBD: self.params.host, self.params.port = addrinfo[-1][-1]
        return await self._connect()

    async def close(self):  # pylint: disable=invalid-overridden-method
        """Stop connection and prevents reconnect.

        :meta private:
        """
        # prevent reconnect:
        self.params.host = None

        if self.connected and self.protocol and self.protocol.transport:
            self.protocol.transport.close()

    def _create_protocol(self, host=None, port=0):
        """Create initialized protocol instance with factory function."""
        protocol = ModbusClientProtocol(
            use_udp=True, framer=self.params.framer, **self.params.kwargs
        )
        protocol.params.host = host
        protocol.params.port = port
        protocol.factory = self
        return protocol

    async def _connect(self):
        """Connect."""
        _logger.debug("Connecting.")
        try:
            endpoint = await self.loop.create_datagram_endpoint(
                functools.partial(
                    self._create_protocol, host=self.params.host, port=self.params.port
                ),
                remote_addr=(self.params.host, self.params.port),
            )
            txt = f"Connected to {self.params.host}:{self.params.port}."
            _logger.info(txt)
            return endpoint
        except Exception as exc:  # pylint: disable=broad-except
            txt = f"Failed to connect: {exc}"
            _logger.warning(txt)
            asyncio.ensure_future(self._reconnect())

    def protocol_made_connection(self, protocol):
        """Notify successful connection.

        :meta private:
        """
        _logger.info("Protocol made connection.")
        if not self.connected:
            self.connected = True
            self.protocol = protocol
        else:
            _logger.error("Factory protocol connect callback called while connected.")

    def protocol_lost_connection(self, protocol):
        """Notify lost connection.

        :meta private:
        """
        if self.connected:
            _logger.info("Protocol lost connection.")
            if protocol is not self.protocol:
                _logger.error(
                    "Factory protocol callback called "
                    "from unexpected protocol instance."
                )

            self.connected = False
            self.protocol = None
            if self.params.host:
                asyncio.create_task(self._reconnect())
        else:
            _logger.error("Factory protocol connect callback called while connected.")

    async def _reconnect(self):
        """Reconnect."""
        txt = f"Waiting {self.delay_ms} ms before next connection attempt."
        _logger.debug(txt)
        await asyncio.sleep(self.delay_ms / 1000)
        self.delay_ms = 2 * self.delay_ms
        return await self._connect()


class ModbusUdpClient(ModbusBaseClient):
    """**ModbusUdpClient**.

    :param host: Host IP address or host name
    :param port: (optional) Port used for communication.
    :param framer: (optional) Framer class.
    :param source_address: (optional) source address of client,
    :param kwargs: (optional) Experimental parameters

    Example::

        from pymodbus.client import ModbusUdpClient

        async def run():
            client = ModbusUdpClient("localhost")

            client.connect()
            ...
            client.close()
    """

    def __init__(
        self,
        host: str,
        port: int = Defaults.UdpPort,
        framer: ModbusFramer = ModbusSocketFramer,
        source_address: typing.Tuple[str, int] = None,
        **kwargs: any,
    ) -> None:
        """Initialize Asyncio Modbus UDP Client."""
        super().__init__(framer=framer, **kwargs)
        self.params.host = host
        self.params.port = port
        self.params.source_address = source_address

        self.socket = None

    @property
    def connected(self):
        """Connect internal.

        :meta private:
        """
        return self.connect()

    def connect(self):
        """Connect to the modbus tcp server.

        :meta private:
        """
        if self.socket:
            return True
        try:
            family = ModbusUdpClient._get_address_family(self.params.host)
            self.socket = socket.socket(family, socket.SOCK_DGRAM)
            self.socket.settimeout(self.params.timeout)
        except socket.error as exc:
            txt = f"Unable to create udp socket {exc}"
            _logger.error(txt)
            self.close()
        return self.socket is not None

    def close(self):
        """Close the underlying socket connection.

        :meta private:
        """
        self.socket = None

    def send(self, request):
        """Send data on the underlying socket.

        :meta private:
        """
        super().send(request)
        if not self.socket:
            raise ConnectionException(str(self))
        if request:
            return self.socket.sendto(request, (self.params.host, self.params.port))
        return 0

    def recv(self, size):
        """Read data from the underlying descriptor.

        :meta private:
        """
        super().recv(size)
        if not self.socket:
            raise ConnectionException(str(self))
        return self.socket.recvfrom(size)[0]

    def is_socket_open(self):
        """Check if socket is open.

        :meta private:
        """
        if self.socket:
            return True
        return self.connect()

    def __str__(self):
        """Build a string representation of the connection."""
        return f"ModbusUdpClient({self.params.host}:{self.params.port})"

    def __repr__(self):
        """Return string representation."""
        return (
            f"<{self.__class__.__name__} at {hex(id(self))} socket={self.socket}, "
            f"ipaddr={self.params.host}, port={self.params.port}, timeout={self.params.timeout}>"
        )
