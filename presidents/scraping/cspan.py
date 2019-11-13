from bs4.element import NavigableString

from presidents.scraping import get_soup, iter_datalist_pairs
from presidents.util import parse_date


def _iter_transcript_paragraph_strings(element):
    for child in element.children:
        if isinstance(child, NavigableString):
            yield str(child)
        else:
            is_ellipses = child.has_attr('class') and ('hidden-full-transcript-ellipses' in child['class'])
            if not is_ellipses:
                yield child.get_text()


def _iter_substantive_strings(strings):
    for string in strings:
        stripped_string = string.strip()
        if stripped_string:
            yield stripped_string


def _fetch_transcript_paragraphs(program_id):
    url = 'https://www.c-span.org/video/?' + program_id + '&action=getTranscript&transcriptType=cc'
    soup = get_soup(url)
    for paragraph in soup.find_all('p'):
        text = ''.join(_iter_substantive_strings(_iter_transcript_paragraph_strings(paragraph)))
        yield ' '.join(text.strip().split())


def fetch(program_id):
    '''
    Scrape C-SPAN transcript from https://www.c-span.org/ by Program ID

    Returns a standard paper/article dict
    '''
    url = 'https://www.c-span.org/video/?' + program_id
    soup = get_soup(url)
    datalist = soup.find(id='more-information').find(class_='details').find('dl')
    details = {k.strip(':'): v for k, v in iter_datalist_pairs(datalist)}
    first_aired_date = ''.join(details['First Aired'].split('|')[:-1])
    return {
        'source': url,
        'text': '\n'.join(_fetch_transcript_paragraphs(program_id)),
        'timestamp': parse_date(first_aired_date).isoformat(),
        'location': details['Location'],
        'category': details['Format'].lower(),
    }
