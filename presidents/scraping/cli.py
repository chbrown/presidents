#!/usr/bin/env python
import sys
import json
import argparse
import logging
# sources (relative imports)
from . import abcnews, cbsnews, cspan, millercenter, tapp, whitehouse

# each command should be a function from an argparse opts object to an iterable
# of standard speech dicts
commands = {
    'abcnews': lambda opts: (abcnews.fetch(page_url) for page_url in opts.args),
    'cbsnews': lambda opts: (cbsnews.fetch(page_url) for page_url in opts.args),
    'cspan': lambda opts: (cspan.fetch(program_id) for program_id in opts.args),
    'millercenter': lambda opts: millercenter.fetch_speeches(),
    'tapp': lambda opts: (tapp.fetch(pid) for pid in opts.args),
    'tapp-inaugurals': lambda opts: tapp.fetch_inaugurals(),
    'tapp-election2016': lambda opts: tapp.fetch_election('2016'),
    'tapp-election2012': lambda opts: tapp.fetch_election('2012'),
    'tapp-election2008': lambda opts: tapp.fetch_election('2008'),
    'tapp-election2004': lambda opts: tapp.fetch_election('2004'),
    'tapp-election1960': lambda opts: tapp.fetch_election('1960'),
    'tapp-transition2017': lambda opts: tapp.fetch_transition('2017'),
    'tapp-transition2009': lambda opts: tapp.fetch_transition('2009'),
    'tapp-transition2001': lambda opts: tapp.fetch_transition('2001'),
    'tapp-pids': lambda opts: tapp.fetch_pids(opts.args),
    'whitehouse': lambda opts: whitehouse.fetch_all(opts.args),
}

verbosity_levels = [logging.WARN, logging.INFO, logging.DEBUG, logging.NOTSET]


def main():
    parser = argparse.ArgumentParser(
        description='Scrape major news outlet articles',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', action='count', default=0,
        help='log extra information (repeat for even more, up to 3)')

    # set up commands
    subparsers = parser.add_subparsers(dest='command', help='Command')
    command_parsers = {k: subparsers.add_parser(k) for k in commands}
    # a couple commands take variable args
    for k in ['abcnews', 'cbsnews', 'cspan', 'tapp', 'tapp-pids', 'whitehouse']:
        command_parsers[k].add_argument('args', nargs='*', help='arguments to command')

    opts = parser.parse_args()

    logging.basicConfig(level=verbosity_levels[opts.verbose])

    command = commands[opts.command]
    for obj in command(opts):
        sys.stdout.write(json.dumps(obj, sort_keys=True, ensure_ascii=False))
        sys.stdout.write('\n')
        sys.stdout.flush()

if __name__ == '__main__':
    main()
