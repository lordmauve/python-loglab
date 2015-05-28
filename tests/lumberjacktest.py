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

from loglab import lumberjack
from loglab import magpie

from magpietests import is_sorted, count_lines

# Enter an S3 bucket name here to test against
S3_BUCKET = 'downloads.nationalstrategies.co.uk'



class ConnectionTest(unittest.TestCase):
    def testConnect(self):
        self.lumberjack = lumberjack.Lumberjack.from_configuration_file('boto.cfg', S3_BUCKET) 


class LumberjackTest(unittest.TestCase):
    def setUp(self):
        self.lumberjack = lumberjack.Lumberjack.from_configuration_file('boto.cfg', S3_BUCKET) 
        self.date = datetime.date(2010, 4, 27)

    def testFindKeys(self):
        """Test that all logfiles for a given date are identified.

        There are 96 logs a day, 4 every hour.
        
        """
        keys = list(self.lumberjack.get_keys(date=self.date))
        self.failUnlessEqual(len(keys), 96)

    def testAcquireLogCached(self):
        """Test that all lines are retrieved from the log cache"""
        lines = count_lines(self.lumberjack.get_log(date=self.date, cachedir='.lj_cache'))

        # FIXME: this is specific to the bucket/date we are testing against
        self.failUnlessEqual(lines, 54760)

    def testAcquireLog(self):
        """Test that we can acquire at least 1000 lines from S3"""
        # window_size is important as this affects how many logs need to be
        # acquired up-front to fill the LogBuffer heap
        lines = self.lumberjack.get_log(date=self.date, window_size=100)
        for i, l in enumerate(lines):
            if i > 1000:
                break
        else:
            self.fail("Expected 1000+ lines, got %d" % i)

    def testLogSort(self):
        """Test that the log retrieved from cache files is sorted."""
        log = self.lumberjack.get_log(date=self.date, cachedir='.lj_cache')
        self.failUnlessEqual(is_sorted(log), 'Sorted')
