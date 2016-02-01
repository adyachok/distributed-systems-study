from report import Report


class ReportCPUStat(Report):

    FILE_PATH = '/proc/stat'
    FILE_OBJ = None

    @classmethod
    def get_data(cls, *args):
        d = cls.get_raw_data()
        d.addCallback(cls.process_cpu_stat)
        return d

    @staticmethod
    def process_cpu_stat(result):
        data = {}
        cpu_data = []
        for line in result.split('\n'):
            if line.startswith('cpu'):
                cpu_data.append(line.split())
        for item in cpu_data:
            cpu = item[0]
            nice, idle, iowait = float(item[1]), float(item[3]), float(item[4])
            usage = (nice + idle) * 100 / (nice + idle + iowait)
            usage = round(usage, 1)
            data[cpu] = usage
        return data
