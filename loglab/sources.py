import heapq
from .lineformats import LogLineParseError, LogLine

__all__ = (
    'LogLineSource', 'LogBuffer', 'OrderedSource'
)


class LogLineSource(object):
    """Reads log lines from an iterable and wraps it in LogLine"""
    def __init__(self, iterable, line_class=LogLine, ignore_invalid=True):
        """Construct a LogLine source that wraps lines from iterable in LogLine,
        skipping lines that do not contain a timestamp if ignore_invalid is True.

        """
        self.iterable = enumerate(iterable)
        self.line_class = line_class
        self.ignore_invalid = ignore_invalid

    def __iter__(self):
        """Return the next parsable log line.

        Raises EOFError when the log is exhausted.

        """
        for i, l in self.iterable:
            try:
                yield self.line_class(l, line_number=i + 1)
            except LogLineParseError:
                if not self.ignore_invalid:
                    raise


class LogBuffer(object):
    """Buffers and sorts a log within a sliding window, to ensure
    strict chronological ordering.

    """
    # This class both does the parsing and ordering of a log, and should
    # be broken down further

    def __init__(self, iterable, window_size=1000):
        """Construct an LogBuffer around an iterable sequence of log lines"""
        self.iterable = iter(iterable)

        self.window_size = window_size
        self.heap = []
        self.refill_heap()

    def refill_heap(self):
        """Ensure there are self.window_length items in the heap,
        if there are enough lines left in the file to do so.

        """
        while len(self.heap) < self.window_size:
            try:
                l = self.iterable.next()
            except StopIteration:
                break
            self.heap.append(l)
        heapq.heapify(self.heap)

    def __iter__(self):
        """Iterate through log lines in sorted order"""
        while True:
            try:
                l = self.iterable.next()
            except StopIteration:
                try:
                    yield heapq.heappop(self.heap)
                except IndexError:
                        raise StopIteration()
            else:
                try:
                    yield heapq.heapreplace(self.heap, l)
                except IndexError:
                        raise StopIteration()


class OrderedSource(object):
    """Wrapper to construct a LogBuffer/LineSource from an iterable"""
    def __init__(self, iterable, window_size=1000, line_class=LogLine, ignore_invalid=True):
        self.iterable = iterable
        self.window_size = window_size
        self.line_class = line_class
        self.ignore_invalid = ignore_invalid

    def __iter__(self):
        source = LogLineSource(self.iterable, line_class=self.line_class, ignore_invalid=self.ignore_invalid)
        log = LogBuffer(source, window_size=self.window_size)
        return iter(log)

