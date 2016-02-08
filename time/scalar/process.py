#!/usr/bin/env python

from twisted.internet import protocol
from twisted.internet.defer import Deferred

from objects.host import HostState
from states.host_fsm import HostFSM



# TODO: create client to notify other processes about changes
# let assume that if avg CPU usage will be more than 5 will be triggered
# deferred which will check some random number and if this number will equal for
# example 5 process will send notification to some randomly selected process

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
# data = HostState.get_whole_stat()
#     avg_load = data['cpu_stat']['cpu']
#     if avg_load > 5:
#         host, port = PROCESSES[0]
#         reactor.connectTCP(host, port, DummyClientFactory())

if __name__ == "__main__":
    fsm = HostFSM()