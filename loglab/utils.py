import sys
from .filters import Filter

__all__ = (
    'LineDisplay', 'RandomLineFilter', 'AssertLogNotEmpty'
)


class LineDisplay(object):
    """Display a count of the number of lines processed.

    A single line display can sum lines through more than one pipeline.
    """

    def __init__(self, iterable):
        self.iterable = self.instrument(iterable)
        self.count = 1

    def __iter__(self):
        """Run the main iterator. Only this instrument will output the total
        number of lines afterwards."""
        for l in self.iterable:
            yield l
        sys.stdout.write("%d lines\n" % self.count)
        sys.stdout.flush()

    def instrument(self, iter):
        """Construct an instrument iterator that counts items through a pipeline"""
        for l in iter:
            if self.count % 1000 == 0:
                sys.stdout.write("%d lines\r" % self.count)
                sys.stdout.flush()
            yield l
            self.count += 1


class RandomLineFilter(Filter):
    """Select a random subset of lines from a log.

    Useful for shortening a 1e6-line logfile for testing.

    """
    skip = 0

    def accept(self, line):
        import random
        if self.skip == 0:
            self.skip = random.randint(0, 15)
            return True
        else:
            self.skip -= 1
            return False


class AssertLogNotEmpty(object):
    """Raises an error when iterated if no lines are received."""
    def __init__(self, iterable):
        self.iterable = iterable

    def __iter__(self):
        haslines = False
        for l in self.iterable:
            haslines = True
            yield l
        if not haslines:
            raise AssertionError("Log was empty")


