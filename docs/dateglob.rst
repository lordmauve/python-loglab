Date-aware Globbing
===================

Loglab includes a system to rapidly select logs matching a certain date range
and a certain set of servers.

We extend the standard shell globbing, to allowing the following identifiers:

* ``*`` - match zero or more characters
* ``SERVER`` - match a server name from a given list only
* ``YYYY`` - match a four-digit year, but only if the complete date is in the date range given.
* ``MM`` - match a two-digit month, but only if the complete date is in the date range given.
* ``DD`` - match a two-digit day of the month, but only if the complete date is in the date range given.

Note that currently, all three date components have to be present in the glob;
date comparison by year only or year and month only are not yet supported.

.. automodule:: loglab.dateglob

.. function:: candidate_logs(source_glob, servers=[], start_date=None, end_date=None)

    Match files on the filesystem that match the glob.

    :param source_glob: The glob string to match.
    :param servers: Server name strings that the SERVER token is allowed to match.
    :param start_date: If given, a Python ``date`` that represents the earliest date to allow.
    :param end_date: If given, a Python ``date`` that represents the latest date to allow.

