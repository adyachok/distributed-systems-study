#!/usr/bin/env python

import platform
import time

from ConfigParser import SafeConfigParser

from twisted.internet import endpoints
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from twisted.internet.task import LoopingCall

from metrics.stat import ReportCPUStat
from metrics.uptime import ReportUptime
from objects.host import HostState
from udp_protocols import NotificationUDPProcessor
from udp_protocols import MunticastNotificationProcessor

# TODO: create client to notify other processes about changes
# let assume that if avg CPU usage will be more than 5 will be triggered
# deferred which will check some random number and if this number will equal for
# example 5 process will send notification to some randomly selected process


parser = SafeConfigParser()
parser.read('config.ini')
defaults = parser.defaults()

TCP_PORT = defaults.get('tcp_port')
UDP_PORT = int(defaults.get('udp_port'))
MULTICAST_GROUP = defaults.get('multicast_group')
MULTICAST_PORT = int(defaults.get('multicast_port'))


def build_metrics(result):
    data = {}
    data['uptime'] = result[0][1]
    data['cpu_info'] = result[1][1]
    data['host'] = platform.node()
    data['timestamp'] = time.time()
    HostState.set_ls()
    HostState.set_host_state_stat(data)
    return data


def get_metrics(result):
    uptime_def = ReportUptime.get_data()
    cpu_def = ReportCPUStat.get_data()
    def_list = DeferredList([uptime_def, cpu_def], consumeErrors=True)
    def_list.addCallback(build_metrics)
    return def_list


class Receiver(protocol.Protocol):

    def dataReceived(self, data):
        HostState.set_ls()
        d = Deferred()
        # d.addCallback(get_metrics)
        d.addCallback(self.process_response)
        d.callback(None)

    def process_response(self, data):
        HostState.set_ls()
        self.transport.write('%s\n' % HostState.get_whole_stat())


class EchoFactory(protocol.Factory):

    def buildProtocol(self, addr):
        return Receiver()


# def check_cpu_load():
#     data = HostState.get_whole_stat()
#     avg_load = data['cpu_stat']['cpu']
#     if avg_load > 5:
#         host, port = PROCESSES[0]
#         reactor.connectTCP(host, port, DummyClientFactory())


def main():
    lc = LoopingCall(get_metrics, None)
    lc.start(2)
    reactor.listenUDP(UDP_PORT, NotificationUDPProcessor())
    reactor.listenMulticast(MULTICAST_PORT,
                            MunticastNotificationProcessor(MULTICAST_GROUP),
                            listenMultiple=True)
    endpoints.serverFromString(reactor, "tcp:21999").listen(EchoFactory())
    reactor.run()


if __name__ == "__main__":
    main()
