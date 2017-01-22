import re
import json
from datetime import datetime

from bs4 import BeautifulSoup, element
# suppress BeautifulSoup warning; I want to use the best available parser, but I don't care which
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

import requests
import requests_cache
requests_cache.install_cache('requests_cache')

base_url = 'http://millercenter.org'
date_regex = r'\((\w+ \d+, \d{4})\)'

def split_title(title):
    date_match = re.search(date_regex, title)
    if date_match:
        title = re.sub(date_regex, '', title).strip()
        date = datetime.strptime(date_match.group(1), '%B %d, %Y')
        return title, date
    else:
        return title, None

def iter_speeches():
    speeches_html = requests.get(base_url + '/president/speeches').text
    soup = BeautifulSoup(speeches_html)
    current_president = None
    for child in soup.find(id="listing").children:
        if child.name == 'h2':
            current_president = child.contents[0].strip()
        elif child.name == 'div':
            for anchor in child.select('.title a'):
                title, date = split_title(anchor.text)
                yield current_president, title, date, anchor['href']

def iter_paragraphs(transcript):
    for child in transcript.children:
        if child.name == 'h2' and child.string == 'Transcript':
            continue
        elif isinstance(child, element.NavigableString):
            yield unicode(child)
        else:
            for subchild in child.children:
                if subchild.name == 'br':
                    pass
                elif isinstance(subchild, element.NavigableString):
                    yield unicode(subchild)
                else:
                    yield subchild.get_text()

for president, title, date, href in iter_speeches():
    speech_html = requests.get(base_url + href).text
    # Lincoln's "Cooper Union Address" has some issues.
    speech_html = speech_html.replace('<div id="_mcePaste" style="position: absolute; left: -10000px; top: 120px; width: 1px; height: 1px; overflow-x: hidden; overflow-y: hidden;">', '<p>')
    soup = BeautifulSoup(speech_html)
    transcript = soup.find(id='transcript')
    # two of the speeches have missing transcripts :(
    if transcript:
        paragraphs = [paragraph.strip() for paragraph in iter_paragraphs(transcript) if not paragraph.isspace()]
        # replace &nbsp; + space with just the space
        text = '\n'.join(paragraphs).replace(u'\xA0 ', ' ')
        timestamp = date.date().isoformat() if date else None
        speech = dict(president=president, title=title, timestamp=timestamp, text=text)
        print json.dumps(speech, sort_keys=True, ensure_ascii=False)
