from report import Report


class ReportUptime(Report):
    FILE_PATH = '/proc/uptime'
    FILE_OBJ = None

    @classmethod
    def get_data(cls, *args):
        d = cls.get_raw_data()
        d.addCallback(cls.process_uptime)
        return d

    @staticmethod
    def process_uptime(result):
        uptime_seconds = float(result.split()[0])
        return uptime_seconds
