import platform
import time

from twisted.internet.defer import Deferred, DeferredList

from metrics.stat import ReportCPUStat
from metrics.uptime import ReportUptime


def build_metrics(result):
    data = {}
    data['uptime'] = result[0][1]
    data['cpu_info'] = result[1][1]
    data['host'] = platform.node()
    data['timestamp'] = time.time()
    # HostState.set_ls()
    # HostState.set_host_state_stat(data)
    return data


def get_metrics(result):
    uptime_def = ReportUptime.get_data()
    cpu_def = ReportCPUStat.get_data()
    def_list = DeferredList([uptime_def, cpu_def], consumeErrors=True)
    def_list.addCallback(build_metrics)
    return def_list
