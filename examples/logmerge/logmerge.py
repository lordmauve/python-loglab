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
import time
import datetime

from loglab.file_sources import GZipLogFile, LogFile
from loglab.adapters import LogMultiplexer
from loglab.date_splitter import LogSplitter
from loglab.utils import LineDisplay
from loglab.filters import DateRangeFilter
from loglab.dateglob import candidate_logs

from optparse import OptionParser
from ConfigParser import RawConfigParser, NoOptionError

from dateglob.dateglob import candidate_logs


def parse_date(d):
    if not d:
        return None
    return datetime.date(*time.strptime(d, '%Y-%m-%d')[:3])


parser = OptionParser(usage="""%prog [options] <sections of config file to process>
       %prog [options] -a""")
parser.add_option('-a', '--all', help="Process all sections from config file", action="store_true")
parser.add_option('-q', '--quiet', help="Don't print the number of log lines processed", action='store_true')
parser.add_option('-c', '--config', help='Job config file (default logs.ini)', default='logs.ini')
parser.add_option('-s', '--start-date', help="Only output logs since DATE (in YYYY-MM-DD format, inclusive)", metavar='DATE')
parser.add_option('-e', '--end-date', help="Only output logs up to DATE (in YYYY-MM-DD format, exclusive)", metavar='DATE')
parser.add_option('-n', '--no-act', help="Don't merge; just print what would be done", action="store_true")

options, args = parser.parse_args()

# args will be a list of the jobs in logs.ini to build

start = parse_date(options.start_date)
end = parse_date(options.end_date)

config = RawConfigParser()
config.read(options.config)

if options.all:
    if args:
        parser.error("Cannot specify both -a and a list of jobs to process")
    else:
        sections = config.sections()
else:
    if not args:
        parser.error("No jobs to process.")
    else:
        sections = args

for section in sections:
    if not config.has_section(section):
        print >>sys.stderr, "No such job", section
        continue

    try:
        dest = config.get(section, 'dest').replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d')
    except NoOptionError:
        print >>sys.stderr, "Job", section, "missing dest"

    try:
        sources = config.get(section, 'sources')
    except NoOptionError:
        print >>sys.stderr, "Job", section, "missing sources"

    try:
        servers = config.get(section, 'servers').split(',')
    except NoOptionError:
        servers = ['']


    WINDOW_SIZE = 5000

    # NB. end is exclusive in the CLI but inclusive in candidate_logs
    # However, we need the log dated end to cover the day before end.
    # So we can use the end from the CLI directly.
    logs = candidate_logs(sources, servers=servers, start_date=start, end_date=end)

    if options.no_act:
        if logs:
            logs.sort()
            print "%s: merge from %d logs:" % (section, len(logs))
            for l in logs:
                print "  " + l
            print "to", dest, '(eg. %s)' % (datetime.date.today().strftime(dest))
        else:
            print "%s: no logs to merge." % section
        continue

    sources = []
    for l in logs:
        if l.endswith('.gz'):
            sources.append(GZipLogFile(l, window_size=WINDOW_SIZE))
        else:
            sources.append(UncompressedLogFile(l, window_size=WINDOW_SIZE))

    source = LogMultiplexer(*sources)

    if not options.quiet:
        print "Splitting %s log..." % section
        print "Initialising %d log buffers..." % len(sources)
        source = LineDisplay(source)

    if start or end:
        source = DateRangeFilter(source, start_date=start, end_date=end)

    splitter = LogSplitter(dest)
    splitter.split(source)
