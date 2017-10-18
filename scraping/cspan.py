from bs4.element import NavigableString
from __init__ import not_empty, strip, get_soup, parse_date, iter_datalist_pairs


def _iter_transcript_paragraph_strings(element):
    for child in element.children:
        if isinstance(child, NavigableString):
            yield unicode(child)
        else:
            is_ellipses = child.has_attr('class') and ('hidden-full-transcript-ellipses' in child['class'])
            if not is_ellipses:
                yield child.get_text()


def _fetch_transcript_paragraphs(program_id):
    url = 'https://www.c-span.org/video/?' + program_id + '&action=getTranscript&transcriptType=cc'
    soup = get_soup(url)
    for paragraph in soup.find_all('p'):
        text = ''.join(filter(not_empty, map(strip, _iter_transcript_paragraph_strings(paragraph))))
        yield ' '.join(text.strip().split())


def fetch(program_id):
    '''
    Scrape C-SPAN transcript from https://www.c-span.org/ by Program ID

    Returns a standard paper/article dict
    '''
    url = 'https://www.c-span.org/video/?' + program_id
    soup = get_soup(url)
    dl = soup.find(id='more-information').find(class_='details').find('dl')
    details = {k.strip(':'): v for k, v in iter_datalist_pairs(dl)}
    first_aired_date = ''.join(details['First Aired'].split('|')[:-1])
    return {
        'source': url,
        'text': '\n'.join(_fetch_transcript_paragraphs(program_id)),
        'timestamp': parse_date(first_aired_date).isoformat(),
        'location': details['Location'],
        'category': details['Format'].lower(),
    }
