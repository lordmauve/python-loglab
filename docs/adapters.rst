Adapters
========

.. automodule:: loglab.adapters

Combining Logs
--------------

Because there are often log files from different servers or even different
processes doing the same job, it is useful to be able to combine these into one
list for sequential processing.

.. autoclass:: LogMultiplexer


Iterate over a LogMultiplexer object to receive log lines from each of the logs
passed in in the constructor. Lines are returned in chronological order if each
of the input logs was in chronological order.


Converting Logs
---------------

Combined Log Format is the de-facto standard for webserver analytics. Most logs
contain a superset of combined log data. To allow logs from different
applications to be processed by one system, a ``LogConverter`` can be used to
convert other line formats to Combined Log Format.

.. autoclass:: LogConverter
