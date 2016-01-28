#!/usr/bin/env python

import os
import platform
import time

from twisted.internet import endpoints
from twisted.internet import fdesc
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList

import utils

# TODO: Write a daemon process which will do:
#	1. Receive UDP packets on a predefined port
#	2. Send UDP packets on predefined ports
#	3. Run own time-consuming logic(inner process)
#	4. On start of send, receive, inner will update own LC
#	   (Local clock) variable.

# Local clock
LC = 0

METRICS_FILES = {'uptime': '/proc/uptime',
                 'cpu_stat': '/proc/stat'}
METRICS_FILES_DESC = {}


def make_non_blocking_fdesc(key=None):
    # Creates non-blocking file descriptors
    if not key:
        for key, file_path in METRICS_FILES.iteritems():
            if key not in METRICS_FILES_DESC:
                if os.path.exists(file_path):
                    desc = open(file_path, 'r')
                    fdesc.setNonBlocking(desc)
                    METRICS_FILES_DESC[key] = desc
    else:
        file_path = METRICS_FILES.get(key)
        if file_path and os.path.exists(file_path):
            desc = open(file_path, 'r')
            fdesc.setNonBlocking(desc)
            METRICS_FILES_DESC[key] = desc


def close_fdesc(key=None):
    # Close file descriptors and removes them from the dictionary
    if not key:
        for key, fdesc in METRICS_FILES_DESC.iteritems():
            fdesc.close()
            del METRICS_FILES_DESC[key]
    else:
        fdesc = METRICS_FILES_DESC.get(key)
        if fdesc:
            fdesc.close()
            del METRICS_FILES_DESC[key]


def check_fdesc(result, key):
    # Check return value of reading from non-blocking file descriptor
    # If error states returned, file descriptor are recreated
        if result in (fdesc.CONNECTION_DONE, fdesc.CONNECTION_DONE):
            close_fdesc(key)
            make_non_blocking_fdesc(key)


def get_uptime(*args):
    d = Deferred()
    file_obj = METRICS_FILES_DESC['uptime']
    result = fdesc.readFromFD(file_obj.fileno(), d.callback)
    file_obj.seek(0)
    check_fdesc(result, 'uptime')
    return d


def get_cpu_usage(*args):
    # http://stackoverflow.com/questions/9229333/how-to-get-overall-cpu-usage-e-g-57-on-linux
    # http://stackoverflow.com/questions/1720816/non-blocking-file-access-with-twisted
    # output:  cpu37 36524 2 12155 14884885 1037 0 22 0 0 0
    d = Deferred()
    file_obj = METRICS_FILES_DESC['cpu_stat']
    result = fdesc.readFromFD(file_obj.fileno(), d.callback)
    file_obj.seek(0)
    check_fdesc(result, 'cpu_stat')
    return d


def build_metrics(result):
    data = {}
    data['uptime'] = result[0][1]
    data['cpu_info'] = result[1][1]
    data['host'] = platform.node()
    data['timestamp'] = time.time()
    return data


def get_metrics(result):
    make_non_blocking_fdesc()
    uptime_def = get_uptime()
    uptime_def.addCallback(utils.process_uptime)
    cpu_def = get_cpu_usage()
    cpu_def.addCallback(utils.process_cpu_stat)
    def_list = DeferredList([uptime_def, cpu_def], consumeErrors=True)
    def_list.addCallback(build_metrics)
    return def_list


class Receiver(protocol.Protocol):
    def __init__(self, *args, **kwargs):
        global LC
        self.lc = LC

    def dataReceived(self, data):
        self.lc += 1
        d = Deferred()
        d.addCallback(get_metrics)
        d.addCallback(self.process_response)
        d.callback(None)

    def process_response(self, data):
        self.lc += 1
        print self.lc
        self.transport.write('%s\n' % data)


class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Receiver()


endpoints.serverFromString(reactor, "tcp:21999").listen(EchoFactory())
reactor.run()

