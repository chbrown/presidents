import re
from datetime import datetime
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from __init__ import not_empty, strip, get_soup, get_html, parse_date, logger

base_url = 'http://www.presidency.ucsb.edu'

def _iter_texts(element):
    '''
    Loop over `element`'s children, treating each child as a paragraph if it's a
    string, or each of that child's children as a paragraph if it's an element.

    And yes, they really do nest a bunch of paragraphs inside a span!
    '''
    for child in element.children:
        # we want to collect contiguous spans of strings or non-block elements as a single paragraph
        if isinstance(child, NavigableString):
            yield unicode(child)
        elif child.name == 'b' or child.name == 'i':
            yield child.get_text()
        elif child.name == 'p':
            yield '\n' + ''.join(_iter_texts(child)) + '\n'
        elif child.name == 'br':
            yield '\n'
        elif child.name == 'sup':
            yield child.get_text()
        elif child.name == 'ol' or child.name == 'ul':
            for text in _iter_texts(child):
                yield text
        elif child.name == 'li':
            yield '\n* ' + child.get_text() + '\n'
        else:
            logger.debug("Unrecognized '.displaytext' child: %r", child)
            for text in _iter_texts(child):
                yield text

def fetch(pid):
    '''
    Fetch single paper from The American Presidency Project website (http://www.presidency.ucsb.edu/)
    and return as standard paper/article dict
    '''
    url = base_url + '/ws/index.php?pid=' + pid
    soup = get_soup(url)
    # the HTML they generate is awkward, to say the least
    author, title = soup.find('title').get_text().split(': ', 1)
    date_string = soup.find('span', class_='docdate').string
    date = datetime.strptime(date_string, '%B %d, %Y')
    timestamp = date.date().isoformat()

    displaytext = soup.find('span', class_='displaytext')
    lines = ''.join(_iter_texts(displaytext)).split('\n')
    text = '\n'.join(filter(not_empty, map(strip, lines)))

    paper = dict(author=author, title=title.strip('.'), timestamp=timestamp, source=url, text=text)

    displaynotes = soup.find('span', class_='displaynotes')
    note = displaynotes.get_text(' ') or None
    if note:
        # remove "Note: " prefix if present
        paper['note'] = re.sub(r'^note:\s+', '', note, flags=re.I)

    return paper

def _get_pids(soup):
    for anchor in soup.select('a[href*="index.php?pid="]'):
        yield re.search(r'pid=(\d+)', anchor['href']).group(1)

def _get_paragraph_lines(p):
    for child in p.children:
        if child.name == 'br':
            continue
        elif isinstance(child, NavigableString):
            yield unicode(child)
        else:
            yield child.get_text()

def _get_candidate_info(info_paragraph):
    '''
    Parse candidate information
    '''
    lines = [line.strip() for line in _get_paragraph_lines(info_paragraph)
        if line.strip() not in (u'Candidacy Declared:', 'Status:', '')]
    name, title, candidacy_declared, status = lines
    return dict(name=name, title=title, candidacy_declared=candidacy_declared, status=status)

def _iter_candidate_categories(links_paragraph):
    '''
    Parse links to speeches / statements / press releases / etc.
    '''
    for anchor in links_paragraph.find_all('a'):
        category = anchor.get_text()
        url = base_url + '/' + anchor['href']
        yield category, url

def fetch_election(year):
    '''
    Fetch all papers related to an election campaign; year should be one of:
    2016, 2012, 2008, 2004, 1960
    '''
    year_html = get_html(base_url + '/' + year + '_election.php')
    if year == '2008':
        # fix weird issue in Fred Thompson's entry
        year_html = year_html.replace(
            'Status: withdrew on <span class="docdate">',
            'Status: <span class="docdate">withdrew on ')
    soup = BeautifulSoup(year_html)
    container = soup.find('td', class_='doctext').find_parent('table')
    for td in container.find_all('td', class_='doctext'):
        paragraphs = td.find_all('p')
        if len(paragraphs) > 0:
            info_paragraph, links_paragraph = paragraphs
            candidate = _get_candidate_info(info_paragraph)
            for category, category_url in _iter_candidate_categories(links_paragraph):
                logger.info('Fetching papers from category "%s"', category)
                category_soup = get_soup(category_url)
                category_pids = _get_pids(category_soup)
                for pid in category_pids:
                    paper = fetch(pid)
                    if candidate['name'] != paper['author']:
                        logger.warn('candidate name "%s" does not match paper author "%s" (%s)',
                            candidate['name'], paper['author'], pid)
                    paper['category'] = category
                    yield paper

def fetch_inaugurals():
    ordinals = ['Zeroth', 'First', 'Second', 'Third', 'Fourth']
    soup = get_soup(base_url + '/inaugurals.php')
    pids = _get_pids(soup)
    # TAPP doesn't title (number) each inaugural distinctly
    authors = dict()
    for pid in pids:
        paper = fetch(pid)
        author = paper['author']
        nth = authors[author] = authors.get(author, 0) + 1
        # TAPP does not use consistent titles; e.g.,
        #   Richard Nixon gets "Oath of Office and Second Inaugural Address"
        #   Lyndon B. Johnson gets "The President's Inaugural Address"
        # So we generate titles consistent with Miller Center's titles
        title = 'Inaugural Address'
        if nth > 1:
            title = ordinals[nth] + ' ' + title
        paper['title'] = title
        yield paper

def fetch_transition(year):
    '''
    Fetch all papers related to a presidential transition; year should be one of:
    2017, 2009, 2001
    '''
    soup = get_soup(base_url + '/transition' + year + '.php')
    for pid in _get_pids(soup):
        paper = fetch(pid)
        yield paper

def fetch_listing(params):
    soup = get_soup(base_url + '/ws/index.php', params=params)
    for pid in _get_pids(soup):
        paper = fetch(pid)
        yield paper
