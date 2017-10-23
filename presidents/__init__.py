from __future__ import division, unicode_literals
import os
import logging
from datetime import date
import pytz
import dateutil.parser
import dateutil.tz

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger('presidents')

# `here` is the directory containing this file
here = os.path.dirname(__file__) or os.curdir
# `root` is the directory containing the "presidents" package
# (i.e., the git repo root)
root = os.path.dirname(here)


def empty(xs):
    return len(xs) == 0


def not_empty(xs):
    return len(xs) != 0


def strip(s):
    '''because str.strip and unicode.strip are not the same'''
    return s.strip()


def uniq(xs):
    seen = set()
    for x in xs:
        if x not in seen:
            yield x
        seen.add(x)


def jaccard_index(xs, ys):
    '''
    Calculate the intersection over the union of xs and ys,
    converting xs and ys to sets if they are not already.
    '''
    xset = set(xs)
    yset = set(ys)
    union = len(xset | yset)
    if union != 0:
        return len(xset & yset) / union
    # if union is empty, the intersection must also be empty,
    # in which case we define the result as 1
    return 1

_excluded_tzname_prefixes = (
    'Etc/',
    'Asia/', 'Indian/', 'Australia/', 'Pacific/',
    'Europe/', 'Atlantic/',
    'Brazil/',
    'Africa/',
    'Antarctica/', 'Arctic/')
tzinfos = {name: dateutil.tz.gettz(name)
           for name in pytz.all_timezones
           if not name.startswith(_excluded_tzname_prefixes)}
# _tz_aliases is a hack for 2-letter abbreviations
_tz_aliases = {'PT': 'US/Pacific',
               'MT': 'US/Mountain',
               'CT': 'US/Central',
               'ET': 'US/Eastern'}
for alias in _tz_aliases:
    tzinfos[alias] = tzinfos[_tz_aliases[alias]]


def parse_date(s, default_tzinfo=None):
    '''
    Parse the string `s` as a standard Python datetime using the dateutil library,
    setting its timezone to `default_tzinfo`
    iff default_tzinfo is provided _and_ `s` does not specify a timezone.
    '''
    date = dateutil.parser.parse(s, fuzzy=True, tzinfos=tzinfos)
    if default_tzinfo is not None:
        logger.debug('Setting timezone for %s to default: %s', date, default_tzinfo)
        date = date.replace(tzinfo=date.tzinfo or default_tzinfo)
    return date


def calculate_election_day(inauguration_date):
    '''
    Calculate the date of Election Day corresponding to the given `inauguration_date`
    date or datetime: the Tuesday after the first Monday of the preceding November.
    '''
    year = inauguration_date.year - 1
    november_1 = date(year, 11, 1)
    # weekday() returns 0 for Monday
    first_monday = date(year, 11, 1 + (7 - november_1.weekday()))
    return date(year, 11, first_monday.day + 1)
