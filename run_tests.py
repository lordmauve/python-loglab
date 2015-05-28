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

"""Script for running tests."""

import sys
import unittest

all_tests = unittest.TestSuite()
loader = unittest.defaultTestLoader

if len(sys.argv) == 1:
    import tests.lumberjacktest
    import tests.magpietests
    all_tests.addTests(loader.loadTestsFromModule(tests.lumberjacktest))
    all_tests.addTests(loader.loadTestsFromModule(tests.magpietests))
else:
    for arg in sys.argv[1:]:
        all_tests.addTest(loader.loadTestsFromName(arg))

testrunner = unittest.TextTestRunner()
testrunner.run(all_tests)
