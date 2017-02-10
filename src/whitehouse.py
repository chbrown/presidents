from __init__ import iter_lines, get_soup, parse_date, logger
from urlparse import urljoin

base_url = 'https://www.whitehouse.gov'

briefing_room_groups = [
    # Speeches & Remarks
    'speeches-and-remarks',
    # Press Briefings
    'press-briefings',
    # Statements & Releases
    'statements-and-releases',
    # Presidential Actions
    'presidential-actions/executive-orders',
    'presidential-actions/presidential-memoranda',
    'presidential-actions/proclamations',
    'presidential-actions/related-omb-material',
    # Legislation
    'pending-legislation',
    'signed-legislation',
    'vetoed-legislation',
    # Nominations & Appointments
    'nominations-and-appointments'
    # Disclosures
    # ... no data yet available
]

def _fetch_page(url):
    soup = get_soup(url)
    # heading_title = soup.find(class_='heading-title')
    # heading_subtitle = soup.find(class_='heading-subtitle')
    press_article_date = soup.find(class_='press-article-date')
    date = press_article_date.get_text()
    title = soup.find(class_='pane-node-title')
    content = soup.find(id='content-start')
    # body = content.select_one('.forall-body.field-type-text-long')
    bodies = content.select('.forall-body')
    text = u'\n'.join(iter_lines(*bodies))
    return {
        'source': url,
        'timestamp': parse_date(date).isoformat(),
        'text': text,
    }


def _iter_group_pages(url):
    '''
    Iterate over (title, url) pairs for a given page (usually called with a root
    briefing-room group page url)
    '''
    soup = get_soup(url)
    view = soup.find(class_='view')
    rows = view.find_all(class_='views-row')
    # list the rows on this page
    for row in rows:
        a = row.find('a')
        page_title = a.get_text()
        page_url = urljoin(base_url, a['href'])
        yield page_title, page_url
    # recurse into the next page
    for a in view.find(class_='pager').find_all('a'):
        if a.get_text() == 'Next':
            next_url = urljoin(base_url, a['href'])
            for page_title, page_url in _iter_group_pages(next_url):
                yield page_title, page_url


def _iter_documents():
    '''
    Iterate over its paragraphs of an article from ABC News
    '''
    # there are multiple articles on a single page when JS is enabled, because
    # ABC eager-loads related articles, but in any case, we just want the first one
    container = soup.find(class_='article-body').find(class_='article-copy')
    for paragraph in container.find_all('p', attrs=dict(itemprop='articleBody')):
        yield paragraph.get_text().strip()

def _fetch_group(briefing_room_group):
    '''
    Page through the listing for the specified briefing_room_group, and fetch
    all its pages
    '''
    # if briefing_room_group not in briefing_room_groups:
    # logger.error('invalid briefing room group: %s', briefing_room_group)
    url = base_url + '/briefing-room/' + briefing_room_group.lstrip('/')
    for title, page_url in _iter_group_pages(url):
        page = _fetch_page(page_url)
        yield dict(title=title, **page)

def fetch_all(selected_briefing_room_groups=briefing_room_groups):
    for briefing_room_group in selected_briefing_room_groups:
        for page in _fetch_group(briefing_room_group):
            yield page
