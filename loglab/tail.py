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
import select
import time


class TailSource(object):
    """Tails a logfile, yielding lines in real time.
    """
    def __init__(self, logfile, from_start=False):
        self.f = open(logfile, 'r')

        self.keeprunning = True

        if from_start:
            # No need to skip the first line
            self.started = True
        else:
            # skip to one byte before the end, in case the file already ends with
            # a newline, as this will ensure the first new line isn't skipped.
            try:
                self.f.seek(-1, os.SEEK_END)
            except IOError:
                self.f.seek(0, os.SEEK_END)

            # skip the first line in case it is incomplete
            self.started = False

    def stop(self):
        self.keeprunning = False

    def __iter__(self):
        """Iterate over lines added to the file since it was opened.

        Blocks until new lines are available to read, so must be wrapped as
        a thread if non-blocking behaviour is required.

        This method takes care not to output a partial line by only outputting
        lines that are terminated by a newline. It also skips the first line as
        it does not know whether this is the start of a line.
        """
        # holder for incomplete final line
        incomplete = ''

        while self.keeprunning:
            # Minimum time to wait for some data to accrue
            #
            # This is necessary so that we're not using CPU time
            # processing very small chunks of data
            time.sleep(2)

            # block until the file has data
            r, w, x = select.select([self.f], [], [self.f])

            if x:
                break

            buf = self.f.read()
            if not buf:
                continue

            # split the block we've read into lines
            #
            # NB. splitlines() has the wrong semantics:
            #
            # '\n'.splitlines() == [''] but '\n'.split('\n') == ['', '']
            #
            ls = buf.split('\n')

            # the first line is part of the same line as in the incomplete buffer
            incomplete += ls.pop(0)

            # if we still haven't received a new line, the incomplete buffer is
            # still incomplete
            if len(ls) == 0:
                # line still incomplete
                continue

            # otherwise, we can output the incomplete buffer (but only if we've read
            # at least one line)
            if self.started and incomplete:
                yield incomplete
                incomplete = ''
            self.started = True

            # The last line has not been terminated by a newline, and so goes
            # into our incomplete line buffer
            #
            # This is why we need split() above - so that if buf ends with a
            # newline, the last item will be the empty string and thus clears
            # the incomplete buffer
            try:
                incomplete = ls.pop()
            except IndexError:
                continue

            # Yield all the remaining (complete) lines.
            for l in ls:
                yield l
