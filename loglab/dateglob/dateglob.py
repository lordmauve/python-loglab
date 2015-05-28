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
import re
import datetime

class PartialMatch(NotImplementedError):
    """We don't support partial matches yet"""


class PatternMatch(object):
    def __init__(self, day=None, month=None, year=None):
        self.day = day
        self.month = month
        self.year = year

    def refine_year(self, year):
        """check if year fits this match; return a new PatternMatch if so, otherwise None"""
        if year is None:
            return self
        if self.year is None or self.year == year:
            return PatternMatch(day=self.day, month=self.month, year=year)
        return None

    def refine_month(self, month):
        """check if month fits this match; return a new PatternMatch if so, otherwise None"""
        if month is None:
            return self
        if self.month is None or self.month == month:
            return PatternMatch(day=self.day, month=month, year=self.year)
        return None

    def refine_day(self, day):
        """check if day fits this match; return a new PatternMatch if so, otherwise None"""
        if day is None:
            return self
        if self.day is None or self.day == day:
            return PatternMatch(day=day, month=self.month, year=self.year)
        return None

    def refine(self, ano):
        match = self.refine_day(ano.day)
        if match:
            match = match.refine_month(ano.month)
        if match:
            match = match.refine_year(ano.year)
        return match

    def date_cmp(self, date):
        if self.day is None and self.month is None and self.year is None:
            #FIXME: 0 is not always right here. We want to imply there's no comparison
            # or "always pass" as matches without dates should pass so they can be tested
            # elsewhere
            return 0

        if self.day is None or self.month is None or self.year is None:
            raise PartialMatch("Partial date not implemented (%r)" % self)
        d = datetime.date(self.year, self.month, self.day)
        return cmp(d, date)

    def __eq__(self, ano):
        if not isinstance(ano, PatternMatch):
            return False
        return self.__dict__ == ano.__dict__

    def __repr__(self):
        args = [self.day, self.month, self.year]
        return 'PatternMatch(%s)' % ', '.join([repr(a) for a in args if a is not None])


def pattern_cmp(pattern, string, servers=[]):
    """Match pattern (a list of parts) against string.

    Return a dictionary of matches, or None if no match"""

    try:
        chunk = pattern[0]
    except IndexError:
        if string == '':
            return PatternMatch()
        return None

    if chunk == 'SERVER':
        for serv in servers:
            if string.startswith(serv):
                match = pattern_cmp(pattern[1:], string[len(serv):], servers)
                if match:
                    return match
        else:
            return None
    elif chunk == 'YYYY':
        year = string[:4]
        if not year.isdigit():
            return None
        match = pattern_cmp(pattern[1:], string[4:], servers)
        if match:
            return match.refine_year(int(year))
        else:
            return None
    elif chunk == 'MM':
        month = string[:2]
        if not month.isdigit():
            return None
        if not (1 <= int(month) <= 12):
            return None
        match = pattern_cmp(pattern[1:], string[2:], servers)
        if match:
            return match.refine_month(int(month))
        else:
            return None
    elif chunk == 'DD':
        day = string[:2]
        if not day.isdigit():
            return None
        if not (1 <= int(day) <= 31):
            return None
        match = pattern_cmp(pattern[1:], string[2:], servers)
        if match:
            return match.refine_day(int(day))
        else:
            return None
    elif chunk == '*':
        for i in xrange(len(string) + 1):
            match = pattern_cmp(pattern[1:], string[i:], servers)
            if match:
                return match
        else:
            return None
    else:
        if not string.startswith(chunk):
            return None
        return pattern_cmp(pattern[1:], string[len(chunk):], servers)


part_re = re.compile(r'\*|SERVER|YYYY|MM|DD')

def pattern_split(glob):
    pattern = []
    last = 0
    for mo in part_re.finditer(glob):
        if mo.start() > last:
            pattern.append(glob[last:mo.start()])
        pattern.append(mo.group(0))
        last = mo.end()

    if last == 0:
        return None

    if last < len(glob) - 1:
        pattern.append(glob[last:])

    return pattern


def pattern_match(glob, string, servers=[]):
    pattern = pattern_split(glob)

    # handle degenerate case where not a pattern
    if pattern is None:
        if glob == string:
            return PatternMatch()
        return None

    return pattern_cmp(pattern, string, servers)


def glob_search(source_glob, servers=[], start_date=None, end_date=None, date_match=PatternMatch()):
    # We solve this recursively by matching against each path component in turn

    parts = source_glob.split('/')
    locked = './' # the part of source_glob that contains no substitutions

    # Roll leading '/' into top part if source glob is absolute
    if source_glob.startswith('/'):
        parts = parts[1:]
        locked = '/'

    while True:
        try:
            top = parts.pop(0)
        except IndexError:
            return []

        pattern = pattern_split(top)

        if pattern is not None:
            break

        locked += top
        if parts:
            if not os.path.isdir(locked):
                return []
            else:
                locked += '/'
                continue
        else:
            if os.path.exists(locked):
                if start_date or end_date:
                    return []
                else:
                    return [locked]
            return []

    # pattern here contains the split parts
    # locked is the directory within which pattern must match
    # parts is the rest of the glob

    matches = []
    for f in os.listdir(locked):
        match = pattern_cmp(pattern, f, servers=servers)

        # combine with what we've already matched
        if match:
            match = date_match.refine(match)

        # determine if match satisfies start_date and end_date
        try:
            if match and start_date and match.date_cmp(start_date) < 0:
                match = None

            if match and end_date and match.date_cmp(end_date) > 0:
                match = None
        except PartialMatch:
            match = None

        if match:
            path = locked + f
            if parts:
                if not os.path.isdir(path):
                    continue
                glob = path + '/' + '/'.join(parts)
                matches += glob_search(glob, servers, start_date, end_date, match)
            else:
                matches.append(path)
    return matches


def candidate_logs(source_glob, servers=[], start_date=None, end_date=None):
    """Search sources as if using a glob but allowing filtering by specific date ranges.

    Implemented are several pattern matches:

    - * - match anything
    - SERVER - match anything in servers
    YYYY, MM and DD - match if these (combined) lie between start_date and end_date.
    """
    return glob_search(source_glob, servers, start_date, end_date)
