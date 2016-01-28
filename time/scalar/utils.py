def process_uptime(result):
    uptime_seconds = float(result.split()[0])
    return uptime_seconds


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