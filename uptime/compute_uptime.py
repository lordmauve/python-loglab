#!/usr/bin/python

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


import datetime
from logtools.magpie import GZipLogFile, LogMultiplexer, Log, LogSanitisationFilter


class LogFile(Log):
    def __init__(self, fname):
        super(LogFile, self).__init__(open(fname))
    

class UnknownStatus(Exception):
    """The state of the server could not be detected from the log line."""


class DowntimeDetector(object):
    def __init__(self, iterable):
        self.iterable = iterable
        self.lasthit = None

    def on_up(self, time):
        """Handle detection of the site being up as of time in seconds since epoch"""

    def on_down(self, time):
        """Handle detection of the site being up as of time in seconds since epoch"""

    def scan(self):
        isup = True
        for l in self.iterable:
            t = l.time()
            if self.lasthit and (t - self.lasthit) > 45:
                if isup:
                    self.on_down(self.lasthit)
                    isup = False
                    
            try:
                up = self.check_line(l)
            except UnknownStatus:
                continue

            if up:
                if not isup:
                    self.on_up(t)
                    isup = True
                self.lasthit = t

#            if up and not isup:
#                self.on_up(l.time())
#            elif not up and isup:
#                self.on_down(l.time())
#            isup = up

    def check_line(self, l):
        if len(l.code) != 3:
            raise UnknownStatus("Invalid HTTP response code")
        if l.code.startswith('4'):
            raise UnknownStatus("Client error - cannot detect server state")
        return not l.code.startswith('5')

class WindowedDowntimeDetector(DowntimeDetector):
    def __init__(self, iterable, window_size=50, threshold=30):
        self.iterable = iterable
        self.window_size = window_size
        self.threshold = threshold

    def scan(self):
        isup = True
        window = [True] * self.window_size
        for l in self.iterable:
            try:
                s = self.check_line(l)
            except UnknownStatus:
                continue
            window = window[1:] + [s]

            up = len([s for s in window if s]) > self.threshold
            if up and not isup:
                self.on_up(l.time())
            elif not up and isup:
                self.on_down(l.time())
            isup = up


class DebuggingDowntimeDetector(DowntimeDetector):
    def on_up(self, time):
        print "up   @ %s" % datetime.datetime.fromtimestamp(time)

    def on_down(self, time):
        print "down @ %s" % datetime.datetime.fromtimestamp(time)


log = LogSanitisationFilter(LogFile('dimitrios/varnishncsa.log'))
scanner = DebuggingDowntimeDetector(log)
scanner.scan()
