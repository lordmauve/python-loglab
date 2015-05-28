Splitting logs by date
======================

loglab only includes one consumer of logs, a utility class that reads log lines
from some source (possibly an ordered, merged, converted chain of filters,
adapters and so on) and saves them to files, each file named with a specific
date.

.. automodule:: loglab.date_splitter

.. autoclass:: LogSplitter
    :members:
