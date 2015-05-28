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

import gzip
import datetime

class LogSplitter(object):
    """Date-based splitting and compressing of logs.

    LogSplitter will read all input lines and write each lines to a file named
    according to out_template, which should be in the format of Python's
    `strftime
    <http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior>`_.

    This will overwrite any logs files that already exist.

    If out_template ends with '.gz' the logs will be gzip-compressed.
    """

    def __init__(self, out_template):
        """Construct a log splitter for splitting logs into files
        matching out_template, which is interpreter in strftime format.
        """
        self.out_template = out_template

    def open_file(self, date):
        if self.out_template.endswith('.gz'):
            return gzip.GzipFile(date.strftime(self.out_template), 'w')
        else:
            return open(date.strftime(self.out_template), 'w')

    def split(self, lines):
        """Split a sequence of lines among log files by date.

        This should only be called once; subsequent calls may overwrite files.

        """
        logs = {} # mapping of date -> open file handle
        for l in lines:
            d = datetime.date.fromtimestamp(l.time())
            try:
                log = logs[d]
            except KeyError:
                log = self.open_file(d)
                logs[d] = log

            log.write(str(l) + '\n')

        for log in logs.values():
            log.close()
