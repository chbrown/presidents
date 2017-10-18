from __init__ import strip, get_soup, parse_date

base_url = 'http://abcnews.go.com'


def _iter_article_paragraphs(soup):
    '''
    Iterate over its paragraphs of an article from ABC News
    '''
    # there are multiple articles on a single page when JS is enabled, because
    # ABC eager-loads related articles, but in any case, we just want the first one
    container = soup.find(class_='article-body').find(class_='article-copy')
    for paragraph in container.find_all('p', attrs=dict(itemprop='articleBody')):
        yield paragraph.get_text().strip()


def fetch(page_url):
    '''
    Given a full ABC News url, or just the partial path, fetch the page and
    return a standard speech dict
    '''
    url = page_url
    if not url.startswith(base_url):
        url = base_url + '/' + url.lstrip('/')
    soup = get_soup(url)
    timestamp_string = soup.find(class_='timestamp').get_text()
    return {
        'source': url,
        'timestamp': parse_date(timestamp_string).isoformat(),
        'text': '\n'.join(_iter_article_paragraphs(soup)),
    }
