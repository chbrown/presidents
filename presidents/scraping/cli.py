import sys
import json
import argparse
import logging
from cytoolz import unique
# sources (relative imports)
from .. import logger
from . import abcnews, cbsnews, cspan, millercenter, tapp, whitehouse

# each command should be a function from an argparse opts object to an iterable
# of standard speech dicts
commands = {
    'abcnews': lambda opts: (abcnews.fetch(page_url) for page_url in opts.args),
    'cbsnews': lambda opts: (cbsnews.fetch(page_url) for page_url in opts.args),
    'cspan': lambda opts: (cspan.fetch(program_id) for program_id in opts.args),
    'millercenter': lambda opts: millercenter.fetch_speeches(),
    'tapp-fetch': lambda opts: (tapp.fetch(pid) for pid in opts.args),
    'tapp-read': lambda opts: tapp.read_from_local_cache(opts.args),
    'tapp-inaugurals': lambda opts: tapp.fetch_inaugurals(),
    'tapp-election-pids': lambda opts: map(int, tapp.fetch_election_pids(*opts.args)),
    'tapp-transition-pids': lambda opts: map(int, tapp.fetch_transition_pids(*opts.args)),
    'tapp-pids': lambda opts: unique(map(int, tapp.fetch_pids(dict(arg.split('=') for arg in opts.args)))),
    'whitehouse': lambda opts: whitehouse.fetch_all(opts.args),
}


def main():
    parser = argparse.ArgumentParser(
        description='Scrape major news outlet articles',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='log extra information (repeat for even more, up to 3)')
    # (none) => WARNING, -v => INFO, -vv => DEBUG, -vvv => NOTSET
    verbosity_levels = [logging.WARNING, logging.INFO, logging.DEBUG, logging.NOTSET]  # [30, 20, 10, 0]

    # set up commands
    subparsers = parser.add_subparsers(dest='command', help='Command')
    command_parsers = {k: subparsers.add_parser(k) for k in commands}
    # a couple commands take variable args
    for k in ['abcnews', 'cbsnews', 'cspan',
              'tapp-fetch', 'tapp-read',
              'tapp-election-pids', 'tapp-transition-pids', 'tapp-pids',
              'whitehouse']:
        command_parsers[k].add_argument('args', nargs='*', help='arguments to command')

    opts = parser.parse_args()

    logging_level = verbosity_levels[opts.verbose]
    logging.basicConfig(level=logging_level)
    logger.setLevel(logging_level)

    command = commands[opts.command]
    for obj in command(opts):
        json_unicode = json.dumps(obj, sort_keys=True, ensure_ascii=False)
        sys.stdout.write(json_unicode.encode('utf-8'))
        sys.stdout.write('\n')
        sys.stdout.flush()


if __name__ == '__main__':
    main()
