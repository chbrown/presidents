from urlparse import urljoin
import requests
# relative imports
from . import get_soup, iter_lines
from .. import logger, parse_date

base_url = 'https://www.whitehouse.gov'


def _fetch_page(url):
    soup = get_soup(url)
    # heading_title = soup.select_one('.heading-title')
    # heading_subtitle = soup.select_one('.heading-subtitle')
    press_article_date = soup.select_one('.press-article-date')
    date = press_article_date.get_text()
    title = soup.select_one('.pane-node-title')
    content = soup.select_one('#content-start')
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
    view = soup.select_one('.view')
    rows = view.select('.views-row')
    # list the rows on this page
    for row in rows:
        a = row.select_one('a')
        page_title = a.get_text()
        page_url = urljoin(base_url, a['href'])
        yield page_title, page_url
    # recurse into the next page
    for a in view.select('.pager a'):
        if a.get_text() == 'Next':
            next_url = urljoin(base_url, a['href'])
            for page_title, page_url in _iter_group_pages(next_url):
                yield page_title, page_url


def _iter_documents(soup):
    '''
    Iterate over its paragraphs of an article from ABC News
    '''
    # there are multiple articles on a single page when JS is enabled, because
    # ABC eager-loads related articles, but in any case, we just want the first one
    container = soup.select_one('.article-body .article-copy')
    for paragraph in container.select('p[itemprop="articleBody"]'):
        yield paragraph.get_text().strip()


def _fetch_group(briefing_room_group):
    '''
    Page through the listing for the specified briefing_room_group, and fetch
    all its pages
    '''
    logger.info('Fetching briefing-room group: %s', briefing_room_group)
    url = base_url + '/briefing-room/' + briefing_room_group.lstrip('/')
    for title, page_url in _iter_group_pages(url):
        try:
            page = _fetch_page(page_url)
            yield dict(title=title, **page)
        except requests.exceptions.TooManyRedirects as exc:
            logger.warn('Failed to fetch "%s": %s', page_url, exc)


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
    # these pages link to https://www.congress.gov/bill/115th-congress/house-bill/...
    # TODO: add parser for those pages and re-include these groups
    #'pending-legislation',
    #'signed-legislation',
    #'vetoed-legislation',
    # Nominations & Appointments
    #'nominations-and-appointments'
    # Disclosures
    # ... no data yet available
]


def fetch_all(selected_briefing_room_groups=None):
    if not selected_briefing_room_groups:
        selected_briefing_room_groups = briefing_room_groups
    for briefing_room_group in selected_briefing_room_groups:
        for page in _fetch_group(briefing_room_group):
            yield page
