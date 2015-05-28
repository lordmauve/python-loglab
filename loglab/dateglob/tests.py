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

from datetime import *
from dateglob import *
import unittest


class MatchTest(unittest.TestCase):
    def testNormalMatch(self):
        self.failUnlessEqual(pattern_match('foo', 'foo'), PatternMatch())
        self.failUnlessEqual(pattern_match('foo', 'bar'), None)

    def testWildcardMatch(self):
        self.failUnlessEqual(pattern_match('f*', 'fooo'), PatternMatch())
        self.failUnlessEqual(pattern_match('f*', 'f'), PatternMatch())
        self.failUnlessEqual(pattern_match('f*bar', 'foobar'), PatternMatch())
        self.failUnlessEqual(pattern_match('f*bar', 'foobared'), None)

    def testSimpleDateMatch(self):
        self.failUnlessEqual(pattern_match('DD', '17'), PatternMatch(day=17))
        self.failUnlessEqual(pattern_match('DD', '34'), None)
        self.failUnlessEqual(pattern_match('MM', '12'), PatternMatch(month=12))

    def testCompexDateMatch(self):
        self.failUnlessEqual(pattern_match('MMDD', '1231'), PatternMatch(month=12, day=31))

    def testNonGreedy(self):
        self.failUnlessEqual(pattern_match('*DD*', '31122010'), PatternMatch(day=31))

    def testMatchRefine(self):
        self.failUnlessEqual(PatternMatch(None, 12, 2010).refine_year(2010), PatternMatch(None, 12, 2010))
        self.failUnlessEqual(PatternMatch(None, 12, 2010).refine_year(2009), None)
        self.failUnlessEqual(PatternMatch(None, 12, 2010).refine_day(10), PatternMatch(10, 12, 2010))
        self.failUnlessEqual(PatternMatch(31, 10, 2009).refine(PatternMatch()), PatternMatch(31, 10, 2009))
        


class GlobTest(unittest.TestCase):
    def failUnlessEqualSet(self, a, b):
        self.failUnlessEqual(set(a), set(b))

    def testStaticPath(self):
        self.failUnlessEqualSet(candidate_logs('/srv'), ['/srv'])
        self.failUnlessEqualSet(candidate_logs('/srv/logs'), ['/srv/logs'])
        self.failUnlessEqualSet(candidate_logs('/srv/logs/webservers/kisch/kisch.core.directoryofchoice.co.uk-nso-access_log-20101023.gz'), ['/srv/logs/webservers/kisch/kisch.core.directoryofchoice.co.uk-nso-access_log-20101023.gz'])

    def testStar(self):
        self.failUnlessEqualSet(candidate_logs('/srv/logs/webserv*'), ['/srv/logs/webservers', '/srv/logs/webservers-2010-09'])

    def testDateStringMatch(self):
        self.failUnlessEqualSet(candidate_logs('/srv/logs/webservers-YYYY-MM'), ['/srv/logs/webservers-2010-09'])

    def testDateStarMatch(self):
        self.failUnlessEqualSet(candidate_logs('/srv/logs/web*e*rs-YYYY-MM*'), ['/srv/logs/webservers-2010-09'])

    def testServerMatch(self):
        self.failUnlessEqualSet(candidate_logs('/srv/logs/SERVER', servers=['dimitrios', 'grishenko']), ['/srv/logs/grishenko', '/srv/logs/dimitrios'])
        self.failUnlessEqualSet(candidate_logs('/srv/logs/SERVER', servers=['dimitrios', 'grish']), ['/srv/logs/dimitrios'])

    def testDateMatch(self):
        self.failUnlessEqualSet(candidate_logs('/srv/logs/webservers/SERVER/SERVER.*-access_log-YYYYMMDD*', servers=['kisch', 'capungo'], start_date=date(2010, 10, 23), end_date=date(2010, 10, 24)), ['/srv/logs/webservers/kisch/kisch.core.directoryofchoice.co.uk-nso-access_log-20101023.gz', '/srv/logs/webservers/kisch/kisch.core.directoryofchoice.co.uk-nso-access_log-20101024.gz', '/srv/logs/webservers/capungo/capungo.core.directoryofchoice.co.uk-nso-access_log-20101023.gz', '/srv/logs/webservers/capungo/capungo.core.directoryofchoice.co.uk-nso-access_log-20101024.gz'])

    def testEndDateMatch(self):
        self.failUnlessEqualSet(candidate_logs('/srv/logs/webservers/SERVER/SERVER.*-access_log-YYYYMMDD*', servers=['kisch'], end_date=date(2010, 10, 22)), ['/srv/logs/webservers/kisch/kisch.core.directoryofchoice.co.uk-nso-access_log-20101021.gz', '/srv/logs/webservers/kisch/kisch.core.directoryofchoice.co.uk-nso-access_log-20101022.gz'])

    def testStartDateMatch(self):
        self.failUnlessEqualSet(candidate_logs('/srv/logs/webservers/SERVER/SERVER.*-access_log-YYYYMMDD*', servers=['kisch'], start_date=date(2010, 10, 31)), ['/srv/logs/webservers/kisch/kisch.core.directoryofchoice.co.uk-nso-access_log-20101031.gz', '/srv/logs/webservers/kisch/kisch.core.directoryofchoice.co.uk-nso-access_log-20101101'])
unittest.main()
