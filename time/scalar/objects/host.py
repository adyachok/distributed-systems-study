class HostState(object):
    """Class persists host state data"""
    _host_state_stat = {}
    _LC = 0

    @classmethod
    def get_ls(cls):
        return cls._LC

    @classmethod
    def set_ls(cls):
        cls._LC += 1

    @classmethod
    def get_host_state_stat(cls):
        return cls._host_state_stat

    @classmethod
    def set_host_state_stat(cls, stat_dict):
        cls._host_state_stat = stat_dict

    @classmethod
    def get_whole_stat(cls):
        data = cls.get_host_state_stat()
        data['local_time'] = cls.get_ls()
        return data
