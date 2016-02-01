import abc
import os

from twisted.internet.defer import Deferred
from twisted.internet.fdesc import CONNECTION_DONE, CONNECTION_LOST
from twisted.internet.fdesc import readFromFD
from twisted.internet.fdesc import setNonBlocking


class Report(object):
    __metaclass__ = abc.ABCMeta

    FILE_PATH = None
    FILE_OBJ = None

    @classmethod
    def make_non_blocking_fdesc(cls):
        """Creates non-blocking file descriptors."""
        if cls.FILE_PATH and os.path.exists(cls.FILE_PATH):
            cls.FILE_OBJ = open(cls.FILE_PATH, 'r')
            setNonBlocking(cls.FILE_OBJ)

    @classmethod
    def close_fdesc(cls):
        """Close file descriptors and removes them from the dictionary."""
        cls.FILE_OBJ.close()

    @classmethod
    def check_fdesc(cls, result):
        """Check return value of reading from non-blocking file descriptor.
        If error states returned, file descriptor are recreated."""
        if result in (CONNECTION_DONE, CONNECTION_DONE):
            cls.close_fdesc()
            cls.make_non_blocking_fdesc()

    @classmethod
    def get_raw_data(cls, *args):
        if not cls.FILE_OBJ:
            cls.make_non_blocking_fdesc()
        d = Deferred()
        file_obj = cls.FILE_OBJ
        result = readFromFD(file_obj.fileno(), d.callback)
        file_obj.seek(0)
        cls.check_fdesc(result)
        return d
