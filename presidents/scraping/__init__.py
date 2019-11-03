import os
import re
import warnings

import requests
import requests_cache
from bs4 import BeautifulSoup
from bs4.element import NavigableString

from .. import logger

requests_cache_filepath = os.getenv('PYTHON_REQUESTS_CACHE', '/tmp/python-requests_cache')
requests_cache.install_cache(requests_cache_filepath)
logger.debug('using HTTP requests cache at %s', requests_cache_filepath)

# suppress BeautifulSoup warning; I want to use the best available parser, but I don't care which
warnings.filterwarnings('ignore', category=UserWarning, module='bs4')


def iter_texts(element):
    '''
    Recurse into a single BeautifulSoup element, generically extracting legible
    text as unicode strings
    '''
    # we want to collect contiguous spans of strings or non-block elements as a single paragraph
    if isinstance(element, NavigableString):
        yield str(element)
    elif element.name == 'li':
        yield '\n'
        yield '* '
        for child in element.children:
            for text in iter_texts(child):
                yield text
        yield '\n'
    elif element.name in {'br', 'hr'}:
        yield '\n'
    elif element.name in {'p', 'div', 'ol', 'ul'}:
        yield '\n'
        for child in element.children:
            for text in iter_texts(child):
                yield text
        yield '\n'
    else:
        for child in element.children:
            for text in iter_texts(child):
                yield text


def iter_lines(*elements):
    '''
    Iterate over all texts in elements using iter_texts(element), merging
    contiguous line breaks, yielding individual lines as unicode strings
    '''
    texts = (text for element in elements for text in iter_texts(element))
    lines = ''.join(texts).split('\n')
    for line in lines:
        stripped_line = line.strip()
        if len(stripped_line) != 0:
            yield stripped_line


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
    content_type = re.search(br'<meta.+charset=([a-z0-9-]+)', response.content, re.I)
    if content_type:
        encoding = content_type.group(1)
        logger.debug('Setting encoding to "%s" from //meta[charset] attribute', encoding)
        response.encoding = encoding
    return response


def get_html(url, **kwargs):
    logger.info('Fetching "%s" %r', url, kwargs)
    response = reencode_response(requests.get(url, **kwargs))
    return response.text


def get_soup(url, **kwargs):
    return BeautifulSoup(get_html(url, **kwargs))
