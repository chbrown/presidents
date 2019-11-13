from datetime import date
from typing import Optional
import logging
import re

import dateutil.parser
import dateutil.tz
import pytz

logger = logging.getLogger(__name__)


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


def parse_date(text: str, default_tzinfo: Optional[str] = None) -> date:
    '''
    Parse the string `text` as a standard Python datetime using the dateutil library,
    setting its timezone to `default_tzinfo`
    iff default_tzinfo is provided _and_ `s` does not specify a timezone.
    '''
    date_instance = dateutil.parser.parse(text, fuzzy=True, tzinfos=tzinfos)
    if default_tzinfo is not None:
        logger.debug('Setting timezone for %s to default: %s', date_instance, default_tzinfo)
        date_instance = date_instance.replace(tzinfo=date_instance.tzinfo or default_tzinfo)
    return date_instance


def calculate_election_day(inauguration_date: date) -> date:
    '''
    Calculate the date of Election Day corresponding to the given `inauguration_date`
    date or datetime: the Tuesday after the first Monday of the preceding November.
    '''
    year = inauguration_date.year - 1
    november_1 = date(year, 11, 1)
    # weekday() returns 0 for Monday
    first_monday = date(year, 11, 1 + (7 - november_1.weekday()))
    return date(year, 11, first_monday.day + 1)


def elide(text: str, max_chars: int = 280) -> str:
    """
    Return a string that is at most `max_chars` long.
    """
    n_chars = len(text)
    if n_chars <= max_chars:
        return text
    # too long; truncate and add ellipsis and total
    summary = f"… ({n_chars:,} characters total)"
    return text[:max_chars - len(summary)] + summary


def slugify(text: str) -> str:
    """
    Simplify `text` into a string containing only lowercase word characters.

    The result will (roughly) match the regex: /^[0-9a-z][0-9a-z_]*[0-9a-z]$/
    """
    # 1. lowercase
    text = text.lower()
    # 2. collapse hyphens separating words
    text = re.sub(r"\b-\b", "", text)
    # 3. replace everything but alphanumerics with underscores
    text = re.sub(r"[^0-9a-z]+", "_", text)
    # 4. trim trailing underscores
    text = text.strip("_")
    return text
