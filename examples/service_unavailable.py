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

"""Classes that consume logs and produce reports"""

import datetime

class ServiceUnavailableReport(object):
    """Log consumer that produces a report of total requests, versus 503 errors."""

    def __init__(self, iterable, interval=1):
        self.iterable = iterable
        self.minute = None
        self.interval = interval

    def scan(self):
        requests = 0
        error503s = 0
        for l in self.iterable:
            t = l.time()
            d = datetime.datetime.fromtimestamp(t)
            minute = d.replace(minute=int(d.minute/self.interval) * self.interval, second=0, microsecond=0)
            if minute != self.minute:
                if self.minute is None:
                    self.minute = minute
                else:
                    while minute >= self.minute + datetime.timedelta(seconds=self.interval * 60):
                        yield self.minute, requests, error503s
                        self.minute += datetime.timedelta(seconds=self.interval * 60)
                        requests = 0
                        error503s = 0

            requests += 1
            if l.code == '503':
                error503s += 1

        if self.minute is not None:
            yield self.minute, requests, error503s

