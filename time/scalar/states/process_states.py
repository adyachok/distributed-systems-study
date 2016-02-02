class Born(object):
    """State implements startup of a process.
    The process sends a requests after initialisation of functionality.
    The request is send to the multicast group.
    If no response after some quantity of tries, the process go in
    the LonelyGrownUp state.
    In the other case process go to the GrownUp state.
    """
    # TODO: 1. Initiate functionality
    # TODO: 2. Send info about self 'born' to multicast group
    # tODO: 3. In case no 'greet' response, continue (N) times
    # TODO: 3. In case no 'greet' at all go to the LonelyGrownUp
    # TODO: 4. In other case -> GrownUp
    pass


class GrownUp(object):
    """A leader is found.
    Process report periodically host state to the leader. A leader
    should return heartbeats to own children.
    Process tracks any cluster changes.
    """
    pass


class LonelyGrownUp(object):
    """This state assumes that is only one working host.
    This way process doesn't report host state anywhere and
    doesn't send any packets in the network automatically.
    However it still in multicast group so every "born" signal
    will be processed and state will be changed to CrownUp.
    """
    pass


class OldBones(object):
    """In case to prevent split-brain situation. The process goes to this
    state. After some quantity of retries to find out connection to other
    parts of cluster and if quantity of subcluster > (50% of the cluster +
    1 host), process should stop own host.
    """
    pass
