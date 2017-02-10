from __init__ import strip, get_soup, parse_date, tzinfos

base_url = 'http://www.cbsnews.com'

def _iter_article_paragraphs(soup):
    '''
    Iterate over its paragraphs of an article from CBS News
    '''
    container = soup.find(id='article-entry')
    for paragraph in container.find_all('p'):
        yield paragraph.get_text().strip()

def fetch(page_url):
    '''
    Given a full CBS News url, or just the partial path, fetch the page and
    return a standard speech dict
    '''
    url = page_url
    if not url.startswith(base_url):
        url = base_url + '/' + url.lstrip('/')
    soup = get_soup(url)
    timestamp_string = soup.find(class_='byline').find(class_='time').get_text()
    return {
        'source': url,
        'timestamp': parse_date(timestamp_string, tzinfos['EST']).isoformat(),
        'text': '\n'.join(_iter_article_paragraphs(soup)),
    }
