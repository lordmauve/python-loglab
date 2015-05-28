# loglab - A library for stream-based log processing
# Copyright (c) 2010 Crown copyright
# 
# This file is part of loglab.
# 
# loglab is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# loglab is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with loglab.  If not, see <http://www.gnu.org/licenses/>.

"""Tools for downloading logfiles from Amazon's S3 CDN."""

import os.path
import datetime
import time
import tempfile
import socket

from ConfigParser import ConfigParser

import boto
from boto.s3.connection import S3Connection

import magpie 
import rfc822

socket.setdefaulttimeout(30)


class LumberjackCache(object):
    """Caching for S3 logs, primarily useful when testing or when
    expecting to process the same logfiles many times.
    
    """

    class CacheMiss(Exception):
        """Raised when a file is not in the cache"""

    def __init__(self, cachedir):
        self.cachedir = cachedir

    def cachefile(self, key):
        parts = [self.cachedir, key.bucket.name] + key.name.split('-')[1:4] + [key.name.replace('/', '-')]
        return os.path.join(*parts)

    def timestamp(self, lastmod):
        return time.mktime(time.strptime(lastmod.split('.')[0], "%Y-%m-%dT%H:%M:%S"))

    def get_from_cache(self, key):
        fname = self.cachefile(key)

        if not os.path.exists(fname):
            raise LumberjackCache.CacheMiss()

        cmtime = os.path.getmtime(fname)

        if not key.last_modified:
            raise LumberjackCache.CacheMiss()
        modified_stamp = self.timestamp(key.last_modified)

        if cmtime < modified_stamp:
            raise LumberjackCache.CacheMiss()

        return open(fname, 'rb')

    def retrieve(self, key):
        fname = self.cachefile(key)
        fdir = os.path.dirname(fname)
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        f = open(fname + '.tmp', 'w+b')
        key.get_file(f)
        f.close()
        os.rename(fname + '.tmp', fname)
        return open(fname, 'rb')

    def open(self, key):
        """Return an open file pointing to a log"""
        try:
            return self.get_from_cache(key)
        except LumberjackCache.CacheMiss:
            return self.retrieve(key)


class LumberjackBatch(object):
    """A batch of S3 logs that cover rougly the same time period.
    
    Batches were intended to allow logs to be sorted with very little
    overhead using merged heaps, but the logs within a batch do not span
    the same time period accurately enough to sort correctly.

    LumberjackBatch is now used purely to open the logfile on demand.
    """

    def __init__(self, keys, cache=None):
        self.keys = keys
        self.cache = cache

    def __iter__(self):
        logs = [magpie.Log(self._download_log(key), line_class=magpie.S3LogLine) for key in self.keys]
        if len(logs) > 1:
            return iter(magpie.LogMultiplexer(*logs))
        return iter(logs[0])

    def _download_log(self, key):
        """Downloads logs and returns a handle to a temporary file"""
        if self.cache:
            return self.cache.open(key)
        temp = tempfile.TemporaryFile()
        key.get_file(temp)
        temp.seek(0)
        return temp


class LumberjackSequence(object):
    """A sequence of LumberjackBatch instances, iterated in order"""
    def __init__(self, batches):
        self.batches = batches

    def __iter__(self):
        for batch in self.batches:
            for l in batch:
                yield l


class Lumberjack(object):
    """Brings down logs - Amazon logs from S3.
    
    S3's logfiles rotate on-the-hour, every hour for the purposes of the
    entries they contain, but are named for a time about 20 minutes after
    the end of the period they cover.

    This means it is very easy to select logfiles that cover a specific day.

    However, there are multiple logfiles covering each hour, and these need to
    be merged together in batches to form a chronological log.
    
    """

    def __init__(self, bucket, key=None, secret=None):
        """Create a LumberJack log fetcher to acquire the latest day's logs from S3 bucket `bucket`
        and concatenates them to a compressed logfile whose name is derived from
        today's date formatted as `date_format`, prefix `prefix`, and extension `extension`.

        """
        if key or secret:
            connection = S3Connection(key, secret)
        else:
            connection = boto.connect_s3()
        self.bucket = connection.get_bucket(bucket)

    def get_keys(self, date=None):
        """Query S3 for keys corresponding to logs newer than date_threshold."""
        if date is None:
            date = datetime.date.today()

        keys = []
        # get logs saved on the day in question
        for key in self.bucket.list(date.strftime("log/access_log-%Y-%m-%d")):
            if key.name.startswith(date.strftime("log/access_log-%Y-%m-%d-00")):
                # skip the logs from the first hour, these don't cover date
                continue
            keys.append((key.name, key))

        # we also need the logs from the first hour of the next day as these cover the last hour of date
        next_day = date + datetime.timedelta(days=1)
        for key in self.bucket.list(next_day.strftime("log/access_log-%Y-%m-%d-00")):
            keys.append((key.name, key))

        keys.sort()
        return [key for mtime, key in keys]

    def batched_keys(self, date=None):
        """Group keys representing logs into batches by the hour"""
        keys = self.get_keys(date)
        batches = []
        lastdate = None
        currentbatch = []
        batches.append(currentbatch)
        for k in keys:
            date = k.name.split('-')[1:5]   # timestamp parts we are interested in
            if lastdate is None or date == lastdate:
                currentbatch.append(k)
            else:
                currentbatch = [k]
                batches.append(currentbatch)
            lastdate = date
        return batches

    def get_log_batched(self, date=None, window_size=30000, cachedir=None):
        """Deprecated: use a system of batches to sort logs into strictly chronological order.
        """
        if cachedir is not None:
            cache = LumberjackCache(cachedir)
        else:
            cache = None
        seq = LumberjackSequence([LumberjackBatch(key, cache=cache) for key in self.batched_keys(date)])
        return magpie.LogBuffer(seq, window_size=window_size)

    def get_log(self, date=None, window_size=30000, cachedir=None):
        """Construct a Magpie iterator representing the access log for the
        given date in strict chronological order.

        Amazon's logs have been found so far to be up to about 1.5 hours out-of-order
        so the window size needs to be large enough to accomodate this.
        """
        if cachedir is not None:
            cache = LumberjackCache(cachedir)
        else:
            cache = None
        seq = LumberjackSequence([LumberjackBatch([key], cache=cache) for key in self.get_keys(date)])
        return magpie.LogBuffer(seq, window_size=window_size)

    @staticmethod
    def from_configuration_file(filename, bucket):
        config = ConfigParser()
        config.read([filename])
        key = config.get('Credentials', 'aws_access_key_id')
        secret = config.get('Credentials', 'aws_secret_access_key')
        return Lumberjack(bucket, key=key, secret=secret)
