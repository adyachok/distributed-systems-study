import socket
import struct

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


class MulticastSender(protocol.DatagramProtocol):
    def __init__(self, data, mcast_ip, mcast_port):
        self.data = data
        self.mcast_ip = mcast_ip
        self.mcast_group = (mcast_ip, mcast_port)

    def startProtocol(self):
        self.transport.joinGroup(self.mcast_ip)
        self.transport.write(self.data, self.mcast_group)
        self.transport.loseConnection()

class MulticastSenderSimple(object):

    def __init__(self, mcast_ip, mcast_port, ttl=1):
        self.mcast_group = (mcast_ip, mcast_port)
        self.ttl = ttl
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.1)
        self.set_ttl()

    def set_ttl(self):
        # Set the time-to-live for messages to 1 so they do not go past the
        # local network segment.
        # https://pymotw.com/2/socket/multicast.html
        ttl = struct.pack('b', self.ttl)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    def send(self, data):
        try:
            self.sock.sendto(data, self.mcast_group)
        except Exception as e:
            print e
        finally:
            self.sock.close()

def send_udp(data, address, port):
    """
    Sends UDP packet without waiting for a response
    :param data: (String) data value which have to be send
    :param address: (String) IP address of a remote host
    :param port: (Integer) Port number of a remote host to connect
    :return: None
    """
    # 0 means every port, we don't care
    reactor.listenUDP(0, UDPsender(data, address, port))


def send_udp_mcast(data, mcast_ip, mcast_port):
    """Sends UDP packet to a multicast group without waiting for a response
    :param data: (String) data value which have to be send
    :param mcast_group: (String) IP of a multicast group
    :return: None
    """
    # 0 means every port, we don't care
    reactor.listenMulticast(0, MulticastSender(data, mcast_ip, mcast_port),
                            listenMultiple=True)
