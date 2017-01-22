#!/usr/bin/env python
import logging
import argparse
import json
from datetime import datetime

from bs4 import BeautifulSoup
from bs4.element import NavigableString
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

import requests
import requests_cache
requests_cache.install_cache('/tmp/python-requests_cache')

logger = logging.getLogger('tapp')

base_url = 'http://www.presidency.ucsb.edu'

def to_unicode(element):
    if isinstance(element, NavigableString):
        return unicode(element)
    else:
        return element.get_text()

def read_displaytext(displaytext):
    # yes, they really do nest a bunch of paragraphs inside a span!
    for child in displaytext.children:
        if isinstance(child, NavigableString):
            yield unicode(child)
        else:
            for subchild in child.children:
                yield to_unicode(subchild)

def read_paper(pid):
    url = base_url + '/ws/index.php?pid=' + pid
    logger.info('Fetching "%s"', url)
    html = requests.get(url).text
    soup = BeautifulSoup(html)
    # the HTML they generate is awkward, to say the least
    author, title = soup.find('title').string.split(': ', 1)
    date_string = soup.find('span', class_='docdate').string
    date = datetime.strptime(date_string, '%B %d, %Y')
    timestamp = date.date().isoformat()

    displaytext = soup.find('span', class_='displaytext')
    paragraphs = read_displaytext(displaytext)
    text = '\n'.join(paragraph.strip() for paragraph in paragraphs if not paragraph.isspace())

    displaynotes = soup.find('span', class_='displaynotes')
    note = displaynotes.get_text() or None

    return dict(author=author, title=title, timestamp=timestamp, source=url, note=note, text=text)

def main():
    commands = dict(fetch=read_paper)

    parser = argparse.ArgumentParser(
        description='Scrape The American Presidency Project website (http://www.presidency.ucsb.edu/)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', action='store_true', help='Log extra information')
    parser.add_argument('command', choices=commands, help='Command')
    parser.add_argument('args', nargs='+', help='Arguments to command')
    opts = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if opts.verbose else logging.WARN)

    command = commands[opts.command]

    for arg in opts.args:
        result = command(arg)
        obj = {k: v for k, v in result.items() if v is not None}
        print json.dumps(obj, sort_keys=True, ensure_ascii=False)

if __name__ == '__main__':
    main()
