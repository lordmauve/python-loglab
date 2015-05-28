import re
import time


__all__ = (
    'LogLineParseError', 'CombinedLogLine', 'ApacheLogLine', 'S3LogLine',
    'LogLine'
)


class LogLineParseError(Exception):
    """Raised when a log line is not in the expected format.

    args[0] is a message
    args[1] is the log line causing the error
    """


def group_names(pattern):
    """Find all named groups in a given regular expression pattern"""
    return [mo.group(1) for mo in re.finditer(r'\(\?P<(\w+)>', pattern)]


class LogLineProperty(object):
    """A view of one field in the log line as part of the whole line.

    When updated, this triggers the log line to be rebuilt.
    """
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance._parsed is None:
            instance._full_parse()
        return instance._parsed.get(self.name, '')

    def __set__(self, instance, value):
        instance._parsed[self.name] = value
        instance._line_dirty = True


class LogLineMetaClass(type):
    """Meta class for log line parser classes.

    This metaclass allows log line formats to be written in a declarative
    style. The regular expressions and descriptors for the LogLine will be
    compliled when the class is defined.

     """

    def __new__(cls, name, bases, dict):
        groups = set(group_names(dict['full_pattern']))
        for b in bases:
            if hasattr(b, 'groups'):
                groups = groups.union(b.groups)

        for k in groups:
            assert k not in dict
            dict[k] = LogLineProperty(k)
        dict['groups'] = groups
        dict['full_pattern'] = re.compile(dict['full_pattern'])
        return type.__new__(cls, name, bases, dict)


class CombinedLogLine(object):
    """Parser/wrapper for a log line in Apache combined log format.

    http://httpd.apache.org/docs/2.2/logs.html#combined

    """

    __metaclass__ = LogLineMetaClass

    name = "Combined Log Format"
    stamp_pattern = re.compile(r'\[(\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4})\]')
    full_pattern = (
        r'^(?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|-|unknown)'
        r'(?P<x_forwarded_for>(?:, ?[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})*)'
        r' - '
        r'(?P<username>\w+|-) '
        r'\[(?P<day>\d{2})/(?P<month>[A-Za-z]{3})/(?P<year>\d{4}):(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}) (?P<tz>[+-]\d{4})\] '
        r'"(?P<verb>[A-Z]+) (?P<req>.*?) (?P<proto>HTTP/1\.[01])" '
        r'(?P<code>[0-9]{3}) '
        r'(?P<size>[0-9]+|-) '
        r'"(?P<ref>.*?)" '
        r'"(?P<ua>.*)"'
    )

    __slots__ = ('_line', '_line_dirty', 'line_number', '_parsed', '_time', 'date')

    def __init__(self, line, line_number=None):
        self._line = line.strip()
        self._line_dirty = False
        self.line_number = line_number
        self._parsed = None

        mo = self.stamp_pattern.search(self.line)
        if not mo:
            raise LogLineParseError("Couldn't extract timestamp from log line", self._line)
        self.date = mo.group(1)

    def _full_parse(self):
        mo = self.full_pattern.match(self._line)
        if not mo:
            err = "Couldn't parse line in %s\n" % self.name + self.line.strip()
            if self.line_number:
                err += '\nat log line %d' % self.line_number
            raise LogLineParseError(err, self._line)
        self._parsed = mo.groupdict()
        return self._parsed

    def time(self):
        """Return date as timestamp"""
        try:
            return self._time
        except AttributeError:
            t, tz = self.date.split(' ')
            #FIXME: parse timezone
            self._time = time.mktime(time.strptime(t, '%d/%b/%Y:%H:%M:%S'))
            return self._time

    def _get_line(self):
        if self._line_dirty:
            self._line = self.as_combined_line()
            self._line_dirty = False
        return self._line

    def _set_line(self, line):
        self._line = line
        self._line_dirty = False
        self._parsed = None

    line = property(_get_line, _set_line)

    def as_combined_line(self):
        """Output this log line again in combined format"""
        if not self._parsed:
            self._full_parse()
        vars = dict([(k, '-') for k in self.groups])
        vars.update(self._parsed)
        if self.x_forwarded_for:
            return '%(ip)s%(x_forwarded_for)s - %(username)s [%(day)s/%(month)s/%(year)s:%(hour)s:%(minute)s:%(second)s %(tz)s] "%(verb)s %(req)s %(proto)s" %(code)s %(size)s "%(ref)s" "%(ua)s"' % vars
        return '%(ip)s - %(username)s [%(day)s/%(month)s/%(year)s:%(hour)s:%(minute)s:%(second)s %(tz)s] "%(verb)s %(req)s %(proto)s" %(code)s %(size)s "%(ref)s" "%(ua)s"' % vars

    def __str__(self):
        return self.line

    def __cmp__(self, ano):
        """Compare by timestamp and then by line number.

        By sorting on line number logs stay in original order where dates are exactly equal.
        """
        return cmp(self.time(), ano.time()) or cmp(self.line_number, ano.line_number)


class ApacheLogLine(CombinedLogLine):
    """This is a parser for the Apache log format that includes an additional
    cookie field after the User-Agent field.

    Because the UA field can contain quotes so we cannot unambiguously
    determine whether the extra field exists. This class attempts to parse
    cookie field and falls back to the CombinedLogLine parser.
    """
    name = "Combined Log Format"
    full_pattern = (
        r'^(?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|-|unknown)'
        r'(?P<x_forwarded_for>(?:, ?[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})*)'
        r' - '
        r'(?P<username>\w+|-) '
        r'\[(?P<day>\d{2})/(?P<month>[A-Za-z]{3})/(?P<year>\d{4}):(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}) (?P<tz>[+-]\d{4})\] '
        r'"(?P<verb>[A-Z]+) (?P<req>.*?) (?P<proto>HTTP/1\.[01])" '
        r'(?P<code>[0-9]{3}) '
        r'(?P<size>[0-9]+|-) '
        r'"(?P<ref>.*?)" '
        r'"(?P<ua>.*)"'
        r' "(?P<cookie>.*\*|-)"'
    )

    def _full_parse(self):
        try:
            return super(ApacheLogLine, self)._full_parse()
        except LogLineParseError:
            self.full_pattern = CombinedLogLine.full_pattern
            return super(ApacheLogLine, self)._full_parse()



class S3LogLine(CombinedLogLine):
    """Implements a parser for the S3 log format as documented at

    http://docs.amazonwebservices.com/AmazonS3/latest/index.html?LogFormat.html
    """

    name = "S3 Log Format"
    full_pattern = (
        r'^(?P<owner>[0-9a-z]+|-) '
        r'(?P<bucket>[a-z0-9.]+|-) '
        r'\[(?P<day>\d{2})/(?P<month>[A-Za-z]{3})/(?P<year>\d{4}):(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}) (?P<tz>[+-]\d{4})\] '
        r'(?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|-|unknown) '
        r'(?P<requester>\w+|-) '
        r'(?P<request>[0-9A-Z]+|-) '
        r'(?P<operation>SOAP.[\w.]+|REST.\w+.\w+|-) '
        r'(?P<key>[^\s]+) '
        r'"(?P<verb>[A-Z]+) (?P<req>[^ ]+) (?P<proto>HTTP/1\.[01])" '
        r'(?P<code>[0-9]{3}) '
        r'(?P<error_code>\w+|-) '
        r'(?P<size>[0-9]+|-) '
        r'(?P<filesize>[0-9]+|-) '
        r'(?P<total_time>[0-9]+|-) '
        r'(?P<turnaround_time>[0-9]+|-) '
        r'"(?P<ref>.*?)" '
        r'"(?P<ua>.*?)"'
        r'( -)?'    # What is this? It's undocumented.
    )

# LogLine as an alias for CombinedLogLine can be used as a default
LogLine = CombinedLogLine
