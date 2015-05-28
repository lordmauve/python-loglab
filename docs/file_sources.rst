File Sources
============

.. automodule:: loglab.file_sources

Webserver logs are usually retrieved from compressed or uncompressed log files
on disk.

Loglab provides these classes for accessing log files on disk as iterables.

.. autoclass:: LogFile

.. autoclass:: DayLogFile

.. autoclass:: GZipLogFile


Tailing a logfile
-----------------

Loglab also includes a source that can retrieve log lines from the end of a
file.

.. automodule:: loglab.tail

.. autoclass:: TailSource

    If ``from_start`` is True, the source will start emitting lines from the
    beginning of the file. Otherwise, it will emit the first full line added
    after the current end of the file.

    .. automethod:: __iter__

