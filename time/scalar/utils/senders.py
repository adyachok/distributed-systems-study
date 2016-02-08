from twisted.internet import protocol
from twisted.internet import reactor


class UDPsender(protocol.DatagramProtocol):
    def __init__(self, data, address, port):
        self.data = data
        self.address = address
        self.port = port

    def startProtocol(self):
        self.transport.write(self.data, (self.address, self.port))
        self.transport.loseConnection()


class UDPMulticastSender(protocol.DatagramProtocol):
    def __init__(self, data, mcast_group):
        self.data = data
        self.mcast_group = mcast_group

    def startProtocol(self):
        self.transport.joinGroup(self.mcast_group)
        self.transport.write(self.data)
        self.transport.loseConnection()


def send_udp(data, address, port):
    """
    Sends UDP packet without waiting for a response
    :param data: (String) data value which have to be send
    :param address: (String) IP address of a remote host
    :param port: (Integer) Port number of a remote host to connect
    :return: None
    """
    # 0 means every port, we don't care
    reactor.listenUDP(0, UDPsender())


def send_udp_mcast(data, mcast_group):
    """Sends UDP packet to a multicast group without waiting for a response
    :param data: (String) data value which have to be send
    :param mcast_group: (String) IP of a multicast group
    :return: None
    """
    # 0 means every port, we don't care
    reactor.listenMulticast(0, UDPMulticastSender(data, mcast_group),
                            listenMultiple=True)
