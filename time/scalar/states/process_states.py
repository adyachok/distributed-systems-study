from transitions import State


class ProcessState(State):
    _name = 'process_state'

    def __init__(self):
        super(ProcessState, self).__init__(self._name)


class Prenatal(ProcessState):
    """Initial process state."""
    _name = 'prenatal'


class Born(ProcessState):
    """State implements startup of a process.
    The process sends a requests after initialisation of functionality.
    The request is send to the multicast group.
    If no response after some quantity of tries, the process go in
    the LonelyGrownUp state.
    In the other case process go to the GrownUp state.
    """
    _name = 'born'


class GrownUp(ProcessState):
    """A leader is found.
    Process report periodically host state to the leader. A leader
    should return heartbeats to own children.
    Process tracks any cluster changes.
    """
    _name = 'grown_up'


class LonelyGrownUp(ProcessState):
    """This state assumes that is only one working host.
    This way process doesn't report host state anywhere and
    doesn't send any packets in the network automatically.
    However it still in multicast group so every "born" signal
    will be processed and state will be changed to CrownUp.
    """
    _name = 'lonely_grown_up'


class OldBones(ProcessState):
    """In case to prevent split-brain situation. The process goes to this
    state. After some quantity of retries to find out connection to other
    parts of cluster and if quantity of subcluster > (50% of the cluster +
    1 host), process should stop own host.
    """
    _name = 'old_bones'


if __name__ == '__main__':
    pass