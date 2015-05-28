Log Line Sources
================

.. automodule:: loglab.sources

Sources take log lines as strings from some iterable and wrap them with
:doc:`LogLine <lineformats>` classes allowing them to be parsed on demand.

.. autoclass:: LogLineSource

Some services may fail to log in an explicitly chronological order, perhaps
because the timestamp marks the start of the request while the log line is only
written when the request finishes.

Because it can be preferable to process log lines in chronological order, a
source can be wrapped with :py:class:`LogBuffer`, which uses a heap to output
lines in ascending order of timestamp, assuming logs are mostly sorted already.

.. autoclass:: LogBuffer

There is a utility class to set up a :py:class:`LogLineSource` and a
:py:class:`LogBuffer` on the same object.

.. autoclass:: OrderedSource
