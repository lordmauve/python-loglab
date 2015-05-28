Filters
=======

Several classes are provided that either include or exclude log lines based on
some test of the parsed line.

Each filter should be passed an iterable of log lines, eg. ::

    >>> filtered = MyFilter(log)
    >>> for l in filtered:
    ...     print l

.. automodule:: loglab.filters

A base class ``Filter`` is provided for writing filters; this allows a new
filter to be defined just by overriding ``accept``:

.. automethod:: Filter.accept


Built-in Filters
----------------

.. autoclass:: DateFilter

.. autoclass:: DateRangeFilter
