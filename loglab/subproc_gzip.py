# loglab - A library for stream-based log processing
# Copyright (c) 2010 Crown copyright
# 
# This file is part of loglab.
# 
# loglab is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# loglab is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with loglab.  If not, see <http://www.gnu.org/licenses/>.

"""Implements most of the funtionality of gzip.open using pipes to gzip.

Because gzip/gunzip can run in separate processes, and are implemented in C, this should
be significantly faster than Python's gzip module, which is a pure-Python implementation.

Python gzip is not in itself multithreaded and would be hampered by the GIL anyway.
"""

import os
import subprocess
import __builtin__

GZIP = '/bin/gzip'


def open(filename, mode='rb'):
    if mode[0] in ['w', 'wb']:
        return Writer(filename, mode)
    elif mode[0] in ['r', 'rb']:
        return Reader(filename, mode)
    else:
        raise NotImplementedError("subproc_gzip.open() does not support mode '%s'" % mode)


class Writer(object):
    def __init__(self, filename, mode):
        self.closed = False
        self.fd = os.open(filename, os.O_WRONLY | os.O_CREAT)
        self.proc = subprocess.Popen([GZIP, '-'], stdin=subprocess.PIPE, stdout=self.fd)
        os.close(self.fd)

        self.write = self.proc.stdin.write
        self.writelines = self.proc.stdin.writelines
        self.flush = self.proc.stdin.flush

    def __del__(self):
        if hasattr(self, 'proc') and not self.closed:
            self.close()

    def close(self):
        if self.closed:
            raise OSError("subproc_gzip.Writer is already closed")
        self.flush()
        self.proc.stdin.close()
        self.proc.wait()
        self.closed = True
        

class Reader(object):
    def __init__(self, filename, mode):
        self.closed = False
        self.proc = subprocess.Popen([GZIP, '-d', '-c', filename], stdout=subprocess.PIPE)

        stdout = os.fdopen(os.dup(self.proc.stdout.fileno()), mode) 
        self.read = stdout.read
        self.readlines = stdout.readlines
        self.next = stdout.next
        self._stdout = stdout

    def __iter__(self):
        return iter(self._stdout) 

    def __del__(self):
        if hasattr(self, 'proc') and not self.closed:
            self.close()

    def close(self):
        if self.closed:
            raise OSError("subproc_gzip.Reader is already closed")
        self._stdout.close()
        self.proc.stdout.close()
        #self.proc.wait()
        self.closed = True
