import logging
import pytz
import dateutil.parser
import dateutil.tz

logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger('presidents')


def empty(xs):
    return len(xs) == 0


def not_empty(xs):
    return len(xs) != 0


def strip(s):
    '''because str.strip and unicode.strip are not the same'''
    return s.strip()


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
    date = dateutil.parser.parse(s, fuzzy=True, tzinfos=tzinfos)
    if default_tzinfo is not None:
        logger.debug('Setting timezone for %s to default: %s', date, default_tzinfo)
        date = date.replace(tzinfo=date.tzinfo or default_tzinfo)
    return date
