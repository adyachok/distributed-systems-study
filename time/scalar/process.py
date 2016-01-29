#!/usr/bin/env python

import platform
import time

from twisted.internet import endpoints
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from twisted.internet.task import LoopingCall

from metrics.stat import ReportCPUStat
from metrics.uptime import ReportUptime
from udp_protocols import NotificationUDPProcessor
from udp_protocols import MunticastNotificationProcessor

# TODO: create client to notify other processes about changes
# let assume that if avg CPU usage will be more than 5 will be triggered
# deferred which will check some random number and if this number will equal for
# example 5 process will send notification to some randomly selected process

PROCESSES = [('localhost', 21998)]
MULTICAST_GROUP = "228.0.0.5"

class HostState(object):
    """Class persists host state data"""
    host_state_stat = {}
    _LC = 0

    @classmethod
    def get_ls(cls):
        return cls._LC

    @classmethod
    def set_ls(cls):
        cls._LC += 1

    @classmethod
    def get_host_state_stat(cls):
        return cls.host_state_stat

    @classmethod
    def set_host_state_stat(cls, stat_dict):
        cls.host_state_stat = stat_dict

    @classmethod
    def get_whole_stat(cls):
        data = cls.get_host_state_stat()
        data['local_time'] = cls.get_ls()
        return data


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
    # reactor.listenUDP(21999, NotificationUDPProcessor())
    # reactor.listenMulticast(22000, MunticastNotificationProcessor(),
    #                         listenMultiple=True)
    endpoints.serverFromString(reactor, "tcp:21999").listen(EchoFactory())
    reactor.run()


if __name__ == "__main__":
    main()