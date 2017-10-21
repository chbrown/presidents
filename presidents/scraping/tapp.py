import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from bs4.element import NavigableString
# relative imports
from . import get_soup, get_html, iter_lines
from .. import logger, parse_date, root
from ..readers import read_ldjson

base_url = 'http://www.presidency.ucsb.edu'

document_categories = [
    (1101, 'Oral: Address - Inaugural'),
    (1102, 'Oral: Address - to Congress (non SOTU)'),
    (1103, 'Oral: Address - State of the Union'),
    (1104, 'Oral: Address - major to the Nation'),
    (1105, 'Oral: Address - Farewell'),
    (1107, 'Oral: Address - Saturday Radio'),
    (1108, 'Oral: Address - Fireside Chats'),
    (1110, 'Oral: Address  - "Inaugural" (Accidental Presidents)'),
    (1113, 'Oral: Address - at College Commencements'),
    (1118, 'Oral: Address - to the UN General Assembly'),
    (1119, 'Oral: Address - to Foreign Legislatures'),
    (1120, 'Oral: Address - Nomination Acceptance'),
    (1128, 'Oral: Remarks - (non categorized)'),
    (1133, 'Oral: Remarks - Toasts'),
    (1135, 'Oral: Remarks - Bill Signings'),
    (1136, 'Oral: Remarks - Bill Vetos'),
    (1137, 'Oral: News Conferences'),
    (1139, 'Oral: News Conferences - Joint'),
    (1140, 'Oral: Interviews'),
    (1141, 'Debates: General Election'),
    (1157, 'Oral: Remarks - Campaign Fundraiser'),
    (1160, 'Oral: Remarks - regarding Executive Nominations'),
    (1161, 'Oral: Remarks - regarding Executive Appointments'),
    (1162, 'Oral: Remarks - regarding Resignations'),
    (2100, 'Written: Messages - (non categorized)'),
    (2110, 'Written: Messages -  to Congress'),
    (2111, 'Written: Messages - Annual Messages (written SOTU)'),
    (2113, 'Written: Messages - Veto Messages'),
    (2114, 'Written: Messages - Pocket Veto Messages'),
    (2115, 'Written: Messages - Budget Messages'),
    (2165, 'Written: Messages -  Farewell Addresses'),
    (2200, 'Written: Memorandums'),
    (2201, 'Written: Memorandums - Pocket Vetos'),
    (2202, 'Written: Memorandums - Determinations'),
    (2210, 'Written: Memorandums - Diplomatic - Memo of Understanding'),
    (2300, 'Written: Executive Orders'),
    (2400, 'Written: Proclamations'),
    (2500, 'Written: Statements - (non categorized)'),
    (2510, 'Written: Statements - Signing Statements'),
    (2511, 'Written: Statements - Veto Statements'),
    (2600, 'Written: Letters - (non categorized)'),
    (2610, 'Written: Letters - to Congress'),
    (2710, 'Written: Notices'),
    (2720, 'Written: Directives'),
    (2800, 'Written: Telegrams - Lincoln (Civil War)'),
    (3001, 'E.O.P.: Press Briefings'),
    (3500, 'OMB: Statements of Administration Policy'),
    (5501, 'Debates: Vice-Presidential'),
    (5502, 'Debates: Primary Elections-Democratic Party'),
    (5503, 'Debates: Primary Elections-Republican Party'),
    (8000, 'Party Platforms'),
]

presidents = [
    (1, 'George Washington'),
    (2, 'John Adams'),
    (3, 'Thomas Jefferson'),
    (4, 'James Madison'),
    (5, 'James Monroe'),
    (6, 'John Quincy Adams'),
    (7, 'Andrew Jackson'),
    (8, 'Martin van Buren'),
    (9, 'William Henry Harrison'),
    (10, 'John Tyler'),
    (11, 'James K. Polk'),
    (12, 'Zachary Taylor'),
    (13, 'Millard Fillmore'),
    (14, 'Franklin Pierce'),
    (15, 'James Buchanan'),
    (16, 'Abraham Lincoln'),
    (17, 'Andrew Johnson'),
    (18, 'Ulysses S. Grant'),
    (19, 'Rutherford B. Hayes'),
    (20, 'James A. Garfield'),
    (21, 'Chester A. Arthur'),
    (22, 'Grover Cleveland'),
    (23, 'Benjamin Harrison'),
    (24, 'Grover Cleveland'),
    (25, 'William McKinley'),
    (26, 'Theodore Roosevelt'),
    (27, 'William Howard Taft'),
    (28, 'Woodrow Wilson'),
    (29, 'Warren G. Harding'),
    (30, 'Calvin Coolidge'),
    (31, 'Herbert Hoover'),
    (32, 'Franklin D. Roosevelt'),
    (33, 'Harry S. Truman'),
    (34, 'Dwight D. Eisenhower'),
    (35, 'John F. Kennedy'),
    (36, 'Lyndon B. Johnson'),
    (37, 'Richard Nixon'),
    (38, 'Gerald R. Ford'),
    (39, 'Jimmy Carter'),
    (40, 'Ronald Reagan'),
    (41, 'George Bush'),
    (42, 'William J. Clinton'),
    (43, 'George W. Bush'),
    (44, 'Barack Obama'),
    (45, 'Donald J. Trump'),
]


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
    # when TAPP uses a timestamp with a 0 day-of-month, convert it to 1
    date_string = re.sub(r'(\w+) 0, (\d{4})', r'\1 1, \2', date_string)
    date = datetime.strptime(date_string, '%B %d, %Y')
    timestamp = date.date().isoformat()

    displaytext = soup.find('span', class_='displaytext')
    text = '\n'.join(iter_lines(displaytext))

    paper = dict(author=author, title=title.strip('.'), timestamp=timestamp, source=url, text=text)

    displaynotes = soup.find('span', class_='displaynotes')
    note = displaynotes.get_text(' ') or None
    if note:
        # remove "Note: " prefix if present
        paper['note'] = re.sub(r'^note:\s+', '', note, flags=re.I)

    return paper


def read_local_cache():
    all_json_path = os.path.join(root, 'data', 'tapp', 'all.local-cache.json')
    return read_ldjson(all_json_path)


def read_from_local_cache(pids):
    # pids should be a list of strings
    pidset = set(pids)
    for paper in read_local_cache():
        _, paper_pid = paper['source'].split('=', 1)
        if paper_pid in pidset:
            yield paper


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


def fetch_election_pids(year):
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
            # Parse links to speeches / statements / press releases / etc.
            for anchor in links_paragraph.find_all('a'):
                category = anchor.get_text()
                category_url = base_url + '/' + anchor['href']
                logger.info('Fetching papers from category "%s"', category)
                category_soup = get_soup(category_url)
                category_pids = _get_pids(category_soup)
                for pid in category_pids:
                    yield pid


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


def fetch_transition_pids(year):
    '''
    Fetch all papers related to a presidential transition; year should be one of:
    2017, 2009, 2001
    '''
    soup = get_soup(base_url + '/transition' + year + '.php')
    for pid in _get_pids(soup):
        yield pid


def _get_records_found(soup):
    # the doctitle we want is an element like:
    # <span ...>Record(s) found: <font ...>7433</font></span>
    for doctitle in soup.select('.doctitle'):
        text = doctitle.get_text()
        if text.startswith('Record(s) found:'):
            return int(text.split(':')[-1])
    return 0


def fetch_pids(params):
    '''
    Fetch all paper IDs for a combination of query params, which can be any of:
    * ty (Document Category, i.e., "type")
    * pres (President, canonical index; e.g., 44 = Obama)
    * month (Month of the year, 01 through 12)
    * daynum (day of the month)
    * year (Year, 4 digits; any of the 229 years from 1789 to 2017)

    args is a list of strings in the form "key=value"
    '''
    params = dict(params, includepress='1', includecampaign='1')

    soup = get_soup(base_url + '/ws/index.php', params=params)
    records_found = _get_records_found(soup)
    logger.debug('fetching {} total pids'.format(records_found))

    page_pids = list(_get_pids(soup))
    logger.debug('found {} pids on current page'.format(len(page_pids)))
    for pid in page_pids:
        yield pid
    if len(page_pids) < records_found:
        last_date = parse_date(soup.select('.listdate')[-1].get_text())
        logger.debug('continuing from last_date: {}'.format(last_date))

        # The TAPP website considers years and month/day separately when searching by year.
        # Or something. Can't quite figure it out. It's weird.

        # get pids to end of year
        params1 = dict(params, yearstart=last_date.year, yearend=last_date.year,
                               monthstart=last_date.month, monthend='12',
                               daystart=last_date.day, dayend='31')
        for pid in fetch_pids(params1):
            yield pid
        # then start at the next year
        params2 = dict(params, yearstart=last_date.year + 1, yearend='2020',
                               monthstart='01', monthend='12',
                               daystart='01', dayend='31')
        for pid in fetch_pids(params2):
            yield pid
