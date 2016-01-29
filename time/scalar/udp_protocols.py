from twisted.internet import protocol


class NotificationUDPProcessor(protocol.DatagramProtocol):

    def datagramReceived(self, datagram, addr):
        # TODO: there should be router, despatched(what to do with notification) logic
        print "Received data: %s from address: %s" % (datagram, addr)
        #self.transport.write(data, (host, port))


class MunticastNotificationProcessor(protocol.DatagramProtocol):

    def __init__(self, multicast_group):
        self.multicast_group = multicast_group

    def startProtocol(self):
        # Join the multicast address, so we can receive replies:
        self.transport.joinGroup(self.multicast_group)
        # Send to 228.0.0.5:8005 - all listeners on the multicast address
        # (including us) will receive this message.
        # self.transport.write('Client: Ping', ("228.0.0.5", 8005))

    def datagramReceived(self, datagram, address):
        print "Datagram %s received from %s" % (repr(datagram), repr(address))
