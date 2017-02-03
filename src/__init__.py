import os
import re
import logging
logger = logging.getLogger('presidents')

import requests
import requests_cache
requests_cache_filepath = os.getenv('PYTHON_REQUESTS_CACHE', '/tmp/python-requests_cache')
requests_cache.install_cache(requests_cache_filepath)
logger.debug('using HTTP requests cache at %s', requests_cache_filepath)

from bs4 import BeautifulSoup
from bs4.element import NavigableString
# suppress BeautifulSoup warning; I want to use the best available parser, but I don't care which
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='bs4')

import pytz
import dateutil.parser
import dateutil.tz

empty = lambda xs: len(xs) == 0
not_empty = lambda xs: len(xs) != 0
# because str.strip and unicode.strip are not the same
strip = lambda s: s.strip()

def get_text(element):
    if isinstance(element, NavigableString):
        return unicode(element)
    else:
        return element.get_text()

def iter_datalist_pairs(dl_soup):
    '''
    Iterate over contents of (<dt>, <dd>) pairs in a <dl>...</dl>
    '''
    term = None
    for child in dl_soup.children:
        if child.name == 'dt':
            term = child.get_text()
        elif child.name == 'dd':
            yield term, child.get_text()

def reencode_response(response):
    '''
    Re-interpret the encoding on the fly if specified as a meta header, e.g.:

        <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=windows-1251">

    If the Content-Type is not specified in the HTTP headers, Python requests
    defaults to ISO-8859-1, which is close to TAPP's usual windows-1251, but not
    quite the same.
    '''
    content_type = re.search(r'<meta.+charset=([a-z0-9-]+)', response.content, re.I)
    if content_type:
        encoding = content_type.group(1)
        logger.debug('Setting encoding to "%s"', encoding)
        response.encoding = encoding
    return response

def get_html(url, **kwargs):
    logger.info('Fetching "%s" %r', url, kwargs)
    response = reencode_response(requests.get(url, **kwargs))
    return response.text

def get_soup(url, **kwargs):
    return BeautifulSoup(get_html(url, **kwargs))

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
_tz_aliases = {'PT': 'US/Pacific', 'MT': 'US/Mountain', 'CT': 'US/Central', 'ET': 'US/Eastern'}
for alias in _tz_aliases:
    tzinfos[alias] = tzinfos[_tz_aliases[alias]]

def parse_date(s, default_tzinfo=None):
    date = dateutil.parser.parse(s, fuzzy=True, tzinfos=tzinfos)
    if default_tzinfo is not None:
        logger.debug('Setting timezone for %s to default: %s', date, default_tzinfo)
        date = date.replace(tzinfo=date.tzinfo or default_tzinfo)
    return date
