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
import glob
import csv
import datetime

from logtools.magpie import GZipLogFile, UncompressedLogFile, LogMultiplexer, LogSanitisationFilter, LineDisplay
from logtools.reports import ServiceUnavailableReport


servers = ['grishenko', 'dimitrios']

logs = []

for s in servers:
    logfiles = glob.glob('varnish/%s/varnishncsa*' % s)
    for l in logfiles:
        if l.endswith('.gz'):
            logs.append(GZipLogFile(l))
        else:
            logs.append(UncompressedLogFile(l))


mux = LogMultiplexer(*logs)
log = LogSanitisationFilter(LineDisplay(mux))
scanner = ServiceUnavailableReport(log)
cw = csv.writer(open('uptime.csv', 'w'))
for minute, requests, error503s in scanner.scan():
    if requests:
        cw.writerow((minute.strftime('%Y-%m-%d %H:%M:00'), requests, 100.0 - float(error503s) * 100.0 / requests))
    else:
        cw.writerow((minute.strftime('%Y-%m-%d %H:%M:00'), requests, '-'))
