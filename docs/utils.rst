Utility Classes
===============

.. automodule:: loglab.utils

The ``loglab.utils`` module provides utility classes that may be helpful when
developing log processing applications.

.. autoclass:: LineDisplay

    .. method:: instrument(iter)

       Return an generator that iterators through the values of `iter`. However
       as a side-effect, the LineDisplay will add the number of lines received
       through this iterator to its total, printing the total at regular
       intervals.

.. autoclass:: RandomLineFilter

.. autoclass:: AssertLogNotEmpty

    This class provides a useful sanity check, especially when working with
    logs merged from multiple sources, when it can be hard to spot that some
    filter or source is not yielding any log lines.
