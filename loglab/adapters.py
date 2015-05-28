from .merge import merge
from .filters import Filter
from .lineformats import CombinedLogLine


__all__ = (
    'LogMultiplexer', 'LogConverter'
)


class LogMultiplexer(object):
    """Produce one merged log from many chronologically-ordered logs."""

    def __init__(self, *logs):
        self.iterable = merge(*logs)

    def __iter__(self):
        return self.iterable


class LogConverter(Filter):
    """Converts log lines to Combined Log Format"""
    def __iter__(self):
        for l in self.iterable:
            yield CombinedLogLine(l.as_combined_line())
