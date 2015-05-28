#!/usr/bin/python2.6

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


"""This package includes generator-based tools for logfile processing.

Each line is wrapped by one of the LogLine wrapper that provides on-demand
parsing. This can be done directly from a logfile using a LogLineSource. Log
and GZipLogFile provide simple wrappers for this process.

All of the processors accept an input iterable as their first argument and
implement the iterator API, allowing processors to be chained.

"""


from .lineformats import (
    LogLineParseError, CombinedLogLine, ApacheLogLine, S3LogLine, LogLine
)
from .adapters import LogMultiplexer, LogConverter
from .utils import LineDisplay, RandomLineFilter, AssertLogNotEmpty
from .sources import LogLineSource, LogBuffer, OrderedSource
from .file_sources import GZipLogFile, DayLogFile, LogFile


# aliases for backwards compatibility
Log = OrderedSource
UncompressedLogFile = LogFile
LogFile = DayLogFile
