from transitions import Machine

from process_states import Born, Prenatal, GrownUp, LonelyGrownUp, OldBones


class HostFSM(object):
    """Model for host states and transitions. States are described in
    states file. This class, however, provides callbacks and inner logic.
    """
    transitions = [{'trigger': 'ready',
                    'source': 'prenatal',
                    'dest': 'born'},
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
        machine = Machine(self,
                          states=[Born(),
                                  Prenatal(),
                                  GrownUp(),
                                  LonelyGrownUp(),
                                  OldBones()],
                          transitions=self.transitions,
                          initial=Prenatal())

    def is_in_bcast_group(self):
        """This method checks if host found out other hosts in broadcast group.
        True is returned when other host are found.
        :return: {boolean}
        """
        # TODO: This method needs checking logic to implement
        return True


if __name__ == "__main__":
    fsm = HostFSM()
    assert fsm.state == 'prenatal'
    fsm.ready()
    assert fsm.state == 'born'
    fsm.sunrise()
    assert fsm.state == 'grown_up'
    fsm.sundown()
    assert fsm.state == 'old_bones'
