.. loglab documentation master file, created by
   sphinx-quickstart on Thu Feb  7 13:50:25 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to loglab's documentation!
==================================

Loglab is a library of components for log filtering and analysis.

In summary, :doc:`log line sources <sources>` are iterable objects that return
:py:class:`LogLines <loglab.lineformats.CombinedLogLine>`; LogLines from these
sources can be merged, filtered and so on.

Contents:

.. toctree::
   :maxdepth: 2

   lineformats
   sources
   file_sources
   adapters
   filters
   dateglob
   utils
   date_splitter


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

