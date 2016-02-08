class HostFSM(object):
    """Model for host states and transitions. States are described in
    states file. This class, however, provides callbacks and inner logic.
    """
    pass


if __name__ == "__main__":
    from process_states import Prenatal, Born, GrownUp, LonelyGrownUp, OldBones
    from process_states import transitions as trans
    import transitions
    fsm = HostFSM()
    machine = transitions.Machine(fsm,
                                  states=[Born(),
                                          Prenatal(),
                                          GrownUp(),
                                          LonelyGrownUp(),
                                          OldBones()],
                                  transitions=trans,
                                  initial=Prenatal())
    print fsm.state
    fsm.ready()
    print fsm.state