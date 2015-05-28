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


import sys
import os
import csv
import time
import datetime

import threading

from logtools.magpie import LogSanitisationFilter, LogLineSource
from logtools.reports import ServiceUnavailableReport
from logtools.tail import TailSource


VARNISHLOG = '/var/log/varnish/varnishncsa.log'
OUTFILE = 'uptime.csv'


class StatLogger(threading.Thread):
    def __init__(self, from_start=False):
	super(StatLogger, self).__init__()
        self.keeprunning = True
        self.f = open(OUTFILE, 'a')
        self.tail = TailSource(VARNISHLOG, from_start=from_start)

    def stop(self):
        self.keeprunning = False
        self.tail.stop()

    def run(self):
        log = LogSanitisationFilter(LogLineSource(self.tail))
        scanner = ServiceUnavailableReport(log)
        cw = csv.writer(self.f)
        scan = iter(scanner.scan())
        while self.keeprunning:
            try:
                minute, requests, error503s = scan.next()
            except StopIteration:
                break
            if requests:
                cw.writerow((minute.strftime('%Y-%m-%d %H:%M:00'), requests, 100.0 - float(error503s) * 100.0 / requests))
            else:
                cw.writerow((minute.strftime('%Y-%m-%d %H:%M:00'), requests, '-'))
            self.f.flush()
        self.f.close()


logger = StatLogger()
logger.start()


try:
    while True:
        # stat both files
        try:
            logstat = os.stat(VARNISHLOG)
        except OSError:
            # ignore temporary errors such as race conditions when the
            # log is rotated
            time.sleep(2)
            continue

        fstat = os.fstat(logger.tail.f.fileno())

        # Check whether the log has been rotated
        if logstat.st_ino != fstat.st_ino:
            logger.stop()
            logger.join()
            logger = StatLogger(from_start=True)
            logger.start()
        time.sleep(30)
finally:
    logger.stop()
