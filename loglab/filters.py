import time

from .lineformats import LogLineParseError


class Filter(object):
    """Base class for log filters"""
    def __init__(self, iterable):
        self.iterable = iter(iterable)

    def __iter__(self):
        for l in self.iterable:
            if self.accept(l):
                yield l

    def accept(self, line):
        """Returns True if a log line should be accepted"""
        raise NotImplementedError("Subclasses must implement this method")


class DateFilter(Filter):
    """Filter to include only log lines whose date matches the given date."""
    def __init__(self, iterable, date):
        self.iterable = iter(iterable)
        self.date = date
        self.prefix = self.date.strftime('%d/%b/%Y')

    def accept(self, line):
        return line.date.startswith(self.prefix)


class DateRangeFilter(Filter):
    """Filter to only yield lines with dates in a given range.

    Either start_date or end_date can be omitted in order to include lines from
    only after, or only before the corresponding date.

    """
    def __init__(self, iterable, start_date=None, end_date=None):
        self.iterable = iterable

        if start_date:
            self.start_date = time.mktime(start_date.timetuple())
        if end_date:
            self.end_date = time.mktime(end_date.timetuple())

        if start_date and end_date:
            self.accept = self.accept_in
        elif start_date:
            self.accept = self.accept_from
        elif end_date:
            self.accept = self.accept_to
        else:
            raise ValueError("Neither start_date nor end_date given")

    def accept_in(self, line):
        return self.start_date <= line.time() < self.end_date

    def accept_from(self, line):
        return self.start_date <= line.time()

    def accept_to(self, line):
        return line.time() < self.end_date
