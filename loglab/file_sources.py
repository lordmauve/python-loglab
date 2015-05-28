import loglab.subproc_gzip as gzip

from .sources import OrderedSource
from .lineformats import LogLine
from .filters import DateFilter

__all__ = (
    'GZipLogFile', 'DayLogFile', 'LogFile'
)


class GZipLogFile(object):
    """Wrapper to construct a LogBuffer from a gzipped file."""
    def __init__(self, filename, window_size=1000, line_class=LogLine, ignore_invalid=True):
        self.filename = filename
        self.window_size = window_size
        self.line_class = line_class
        self.ignore_invalid = ignore_invalid

    def open_file(self):
        self.file = gzip.open(self.filename)
        return self.file

    def close(self):
        try:
            self.file.close()
        except AttributeError:
            pass

    def __iter__(self):
        f = self.open_file()
        return iter(OrderedSource(f, window_size=self.window_size, line_class=self.line_class, ignore_invalid=self.ignore_invalid))


class DayLogFile(object):
    """Wrapper around the above for outputting a filtered, sorted logfile"""
    def __init__(self, filename, date):
        self.logfile = gzip.open(filename, 'r')
        self.filename = filename
        self.date = date

    def __iter__(self):
        return iter(DateFilter(OrderedSource(self.logfile), date=self.date))


class LogFile(OrderedSource):
    def __init__(self, fname, window_size=1000,
            line_class=LogLine, ignore_invalid=True):
        super(LogFile, self).__init__(
            open(fname), window_size, line_class, ignore_invalid
        )

