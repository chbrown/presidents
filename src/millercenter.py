import re
from datetime import datetime
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import requests
from __init__ import get_soup, parse_date

base_url = 'http://millercenter.org'

def _split_title(title):
    date_regex = r'\((\w+ \d+, \d{4})\)'
    date_match = re.search(date_regex, title)
    if date_match:
        title = re.sub(date_regex, '', title).strip()
        date = datetime.strptime(date_match.group(1), '%B %d, %Y')
        return title, date
    else:
        return title, None

def _iter_speeches():
    soup = get_soup(base_url + '/president/speeches')
    current_author = None
    for child in soup.find(id='listing').children:
        if child.name == 'h2':
            current_author = child.contents[0].strip()
        elif child.name == 'div':
            for anchor in child.select('.title a'):
                title, date = _split_title(anchor.text)
                yield current_author, title, date, anchor['href']

def _iter_paragraphs(transcript):
    for child in transcript.children:
        if child.name == 'h2' and child.string == 'Transcript':
            continue
        elif isinstance(child, NavigableString):
            yield unicode(child)
        else:
            for subchild in child.children:
                if subchild.name == 'br':
                    pass
                elif isinstance(subchild, NavigableString):
                    yield unicode(subchild)
                else:
                    yield subchild.get_text()

def fetch_speeches():
    for author, title, date, href in _iter_speeches():
        speech_url = base_url + href
        speech_html = requests.get(speech_url).text
        # Lincoln's "Cooper Union Address" has some issues :(
        speech_html = speech_html.replace('<div id="_mcePaste" style="position: absolute; left: -10000px; top: 120px; width: 1px; height: 1px; overflow-x: hidden; overflow-y: hidden;">', '<p>')
        soup = BeautifulSoup(speech_html)
        transcript = soup.find(id='transcript')
        # two of the speeches have missing transcripts :(
        if transcript:
            paragraphs = [paragraph.strip() for paragraph in _iter_paragraphs(transcript) if not paragraph.isspace()]
            # replace &nbsp; + space with just the space
            text = '\n'.join(paragraphs).replace(u'\xA0 ', ' ')
            timestamp = date.date().isoformat() if date else None
            yield {
                'author': author,
                'title': title,
                'timestamp': timestamp,
                'text': text,
                'source': speech_url,
            }
