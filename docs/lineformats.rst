Log lines and line formats
==========================

.. automodule:: loglab.lineformats

Each line format to parse is encapsulated by a LogLine class, which defines a
regular expression used to parse the line.

There is also the facility to use a "quick" regular expression to parse the
date and time of the log line, in order to more quickly filter log lines by date.

Log lines can be used to parse a line::

    >>> line = LogLine(l)
    >>> line.verb
    'GET'
    >>> line.req
    '/'

Log lines are also mutable, though the output line format is cooerced to
combined format::

    >>> line.verb = 'POST':
    >>> str(line)
    '127.0.0.1 - [28/Jan/2012 15:37:03 +00:00] "POST / HTTP/1.0" 200 597 "-" "-"'


New log line formats can be defined by extending :py:class:`CombinedLogLine`;
such a line format needs only override these three properties:


.. py:attribute:: LogLine.name

    A human-readable name for the line format.

.. py:attribute:: LogLine.stamp_pattern

    A *compiled regular expression object* that will match the date part of the line.

.. py:attribute:: LogLine.full_pattern

    A regular expression *string* that will match the line. The regular
    expression should use named groups; these groups become properties of a
    parsed line instance.


Of course, other properties can be overriden for performance when analysing
large log files.


LogLine classes
----------------

.. autoclass:: CombinedLogLine
    :members:

.. autoclass:: LogLine

.. autoclass:: ApacheLogLine

.. autoclass:: S3LogLine
