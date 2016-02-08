import os
from ConfigParser import SafeConfigParser

from transitions import Machine
from twisted.internet import endpoints
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from process_states import Born, Prenatal, GrownUp, LonelyGrownUp, OldBones
from utils.metrics_processor import get_metrics
from utils.receivers import NotificationUDPProcessor
from utils.receivers import MunticastNotificationProcessor
from utils.receivers import EchoFactory


ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def get_config_parser():
    parser = SafeConfigParser()
    parser.read(os.path.join(ROOT_DIR, 'config.ini'))
    return parser


class HostFSM(object):
    """Model for host states and transitions. States are described in
    states file. This class, however, provides callbacks and inner logic.
    """
    transitions = [{'trigger': 'ready',
                    'source': 'prenatal',
                    'dest': 'born',
                    'before': ['initiate', 'born']},
                   {'trigger': 'sunrise',
                    'source': 'born',
                    'dest': 'grown_up',
                    'conditions': ['is_in_bcast_group']},
                   {'trigger': 'sunrise',
                    'source': ['born', 'grown_up'],
                    'dest': 'lonely_grown_up',
                    'unless': ['is_in_bcast_group']},
                   {'trigger': 'sundown',
                    'source': ['grown_up', 'lonely_grown_up'],
                    'dest': 'old_bones'}]

    def __init__(self):
        self._in_mcast_group = False
        Machine(self,
                states=[Born(),
                        Prenatal(),
                        GrownUp(),
                        LonelyGrownUp(),
                        OldBones()],
                transitions=self.transitions,
                initial=Prenatal())
        from twisted.internet.defer import Deferred
        d = Deferred()
        d.addCallback(self.ready)
        d.addCallback(self.get_state)
        reactor.callLater(.1, d.callback, None)
        reactor.run()

    def is_in_mcast_group(self):
        """This method checks if host found out other hosts in multicast group.
        True is returned when other host are found.
        :return: {boolean}
        """
        # TODO: This method needs checking logic to implement
        return self._in_mcast_group

    def initiate(self, data):
        """Parses configuration values and adds them to the object.
        Method initiate Born state of HostFSM.
        This callback is triggered before Born state.
        """
        self._parse_config()

    def _parse_config(self):
        parser = get_config_parser()
        defaults = parser.defaults()
        self.TCP_PORT = defaults.get('tcp_port')
        self.UDP_PORT = int(defaults.get('udp_port'))
        self.MULTICAST_GROUP = defaults.get('multicast_group')
        self.MULTICAST_PORT = int(defaults.get('multicast_port'))

    def born(self, data):
        """Method initiate TCL and UDP listeners."""
        lc = LoopingCall(get_metrics, None)
        lc.start(2)
        reactor.listenUDP(self.UDP_PORT, NotificationUDPProcessor())
        reactor.listenMulticast(self.MULTICAST_PORT,
                                MunticastNotificationProcessor(self.MULTICAST_GROUP),
                                listenMultiple=True)
        endpoints.serverFromString(reactor, "tcp:21999").listen(EchoFactory())

    def check_mcast_group(self, data):
        # TODO: add multicast group check and going to other states
        self.sunrise()
        return

    def get_state(self, data):
        print self.state


if __name__ == "__main__":
    fsm = HostFSM()
    # assert fsm.state == 'prenatal'
    # fsm.ready()
    # assert fsm.state == 'born'
    # fsm.sunrise()
    # assert fsm.state == 'grown_up'
    # fsm.sundown()
    # assert fsm.state == 'old_bones'
