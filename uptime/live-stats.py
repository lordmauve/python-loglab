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
import datetime

LOGFILE = '/home/mauve/uptime/uptime.csv'

f = open(LOGFILE, 'r')
try:
	f.seek(-4096, os.SEEK_END)
except IOError:
	f.seek(0)

ls = f.read().split('\n')
if len(ls) > 2:
	t, hits, error503 = ls[-2].split(',')
	date = datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:00')
	if (datetime.datetime.now() - date) > datetime.timedelta(seconds=150):
		print >>sys.stderr, "Uptime log is out of date. Is log analyser still running?"
		sys.exit(1)
	print "Date:", repr(t)
	print "Hits:", hits
	print "Error503:", error503
