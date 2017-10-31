from __future__ import division, unicode_literals
import os
import logging
from datetime import date
import pytz
import dateutil.parser
import dateutil.tz

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('presidents')

# `here` is the directory containing this file
here = os.path.dirname(__file__) or os.curdir
# `root` is the directory containing the "presidents" package
# (i.e., the git repo root)
root = os.path.dirname(here)


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


def _iter_tzinfos():
    excluded_tzname_prefixes = (
        'Etc/',
        'Asia/', 'Indian/', 'Australia/', 'Pacific/',
        'Europe/', 'Atlantic/',
        'Brazil/',
        'Africa/',
        'Antarctica/', 'Arctic/')
    for name in pytz.all_timezones:
        if not name.startswith(excluded_tzname_prefixes):
            yield name, dateutil.tz.gettz(name)

    # tz_aliases is a hack for 2-letter abbreviations
    tz_aliases = [
        ('PT', 'US/Pacific'),
        ('MT', 'US/Mountain'),
        ('CT', 'US/Central'),
        ('ET', 'US/Eastern')]
    for alias, name in tz_aliases:
        yield alias, dateutil.tz.gettz(name)

tzinfos = dict(_iter_tzinfos())


def parse_date(text, default_tzinfo=None):
    '''
    Parse the string `text` as a standard Python datetime using the dateutil library,
    setting its timezone to `default_tzinfo`
    iff default_tzinfo is provided _and_ `s` does not specify a timezone.
    '''
    date_object = dateutil.parser.parse(text, fuzzy=True, tzinfos=tzinfos)
    if default_tzinfo is not None:
        logger.debug('Setting timezone for %s to default: %s', date_object, default_tzinfo)
        date_object = date_object.replace(tzinfo=date_object.tzinfo or default_tzinfo)
    return date_object


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
