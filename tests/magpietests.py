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

import os
import os.path

import unittest
import datetime
import gzip

from loglab import magpie
from heapq import merge

TESTLOG = 'tests/logs/testlog1.gz'
TESTLOG2 = 'tests/logs/testlog2.gz'  # specially constructed log needs a window size of greater than 150 for correct sorting
S3_TESTLOG = 'tests/logs/s3testlog.gz'
JUNKLOG = 'tests/logs/junklog'


def is_sorted(log):
    """Returns the string 'Sorted' if the string is sorted, or a description
    of which fields are out of order if not."""
    last = None
    for l in log:
        if last is not None:
            if not (l.date >= last):
                return l.date + " is earlier than " + last
        last = l.date
    if last is None:
        raise ValueError("Empty iterator is not testable")
    return 'Sorted'


def count_lines(log):
    i = 0
    for l in log:
        i += 1
    return i


class LogLineTest(unittest.TestCase):
    """Test parsing of Combined Log Format lines"""
    def testEmptyLogLine(self):
        self.failUnlessRaises(magpie.LogLineParseError, magpie.CombinedLogLine, '')

    def testLogParse(self):
        log = magpie.GZipLogFile(TESTLOG, line_class=magpie.ApacheLogLine)
        uas = set()
        for l in log:
            uas.add(l.ua)

        # 58 is confirmed by running 
        # gunzip -c tests/logs/testlog1.gz | sed -e 's/.*[1-5][0-9][0-9] [0-9-][0-9]* "[^"]*" "\([^"]*\)".*/\1/' | sort -u | wc -l
        self.failUnlessEqual(len(uas), 58)

    def testLogFail(self):
        f = open(JUNKLOG)

        def parse_logline(l):
            line = magpie.LogLine(l)
            line._full_parse()

        for l in f:
            self.failUnlessRaises(magpie.LogLineParseError, parse_logline, l)
        f.close()


class S3LogLineTest(unittest.TestCase):
    """Test parsing of S3 log lines"""
    def setUp(self):
        self.log = magpie.GZipLogFile(S3_TESTLOG, line_class=magpie.S3LogLine)

    def testLogParse(self):
        uas = set()
        for l in self.log:
            uas.add(l.ua)

        self.failUnlessEqual(len(uas), 286)

    def testLogConversion(self):
        log = magpie.LogConverter(self.log)
        uas = set()
        for l in log:
            uas.add(l.ua)

        self.failUnlessEqual(len(uas), 286)
            


class LogBufferTest(unittest.TestCase):
    def testBufferLog(self):
        """Tests that the log buffer extracts lines"""
        buf = magpie.GZipLogFile(TESTLOG)
        self.failIfEqual(count_lines(buf), 0)

    def testSortLog(self):
        """Tests that a buffered log is in monotonically increasing date order"""
        buf = magpie.GZipLogFile(TESTLOG)
        self.failUnless(is_sorted(buf))

    def testWindowSize(self):
        """Test that larger window sizes sort less well-ordered logs"""
        # this log should not sort with the window size set to 100
        buf = magpie.GZipLogFile(TESTLOG2, window_size=100)
        self.failIfEqual(is_sorted(buf), 'Sorted')

        # it should sort with a window size of 200
        buf = magpie.GZipLogFile(TESTLOG2, window_size=150)
        self.failUnlessEqual(is_sorted(buf), 'Sorted')


class DateFilterTest(unittest.TestCase):
    def setUp(self):
        self.buf = magpie.GZipLogFile(TESTLOG)

    def testDateFilter(self):
        """Test that log lines can be extracted from a log"""
        log = magpie.DateFilter(self.buf, date=datetime.date(2010, 4, 24))
        self.failIfEqual(count_lines(log), 0)

    def testDateFilter2(self):
        """Check that no lines match for a different date"""
        log = magpie.DateFilter(self.buf, date=datetime.date(2010, 4, 25))
        self.failUnlessEqual(count_lines(log), 0)


class LogFileTest(unittest.TestCase):
    def setUp(self): 
        self.log = magpie.GZipLogFile(TESTLOG)

    def testLogFile(self):
        """Test that a logfile outputs lines"""
        self.failUnlessEqual(count_lines(self.log), 4999)


class MergeTest(unittest.TestCase):
    """Test merging logs"""
    def setUp(self):
        log1 = magpie.GZipLogFile(TESTLOG)
        log2 = magpie.GZipLogFile(TESTLOG2)
        self.merged = merge(log1, log2)

    def testSorted(self):
        """Check that the sorted logs stay sorted when merged"""
        self.failUnlessEqual(is_sorted(self.merged), 'Sorted')

    def testLineCount(self):
        """Check that the sorted logs output all of the lines from the individual logs"""
        self.failUnlessEqual(count_lines(self.merged), 6998)


# Need to test:
#  LogSanitisationFilter
