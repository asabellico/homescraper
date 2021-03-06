"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = homescraper.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This skeleton file can be safely removed if not needed!

References:
    - https://setuptools.readthedocs.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import logging
import os
import sys
import time

from homescraper import __version__
from homescraper.scraper import scrape_apartments
from homescraper.config import parse_config

__author__ = "Alessandro Sabellico"
__copyright__ = "Alessandro Sabellico"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Just a Fibonacci demonstration")
    parser.add_argument(
        "--version",
        action="version",
        version="homescraper {ver}".format(ver=__version__),
    )
    parser.add_argument(dest="config_path", help="Query config path", type=str, metavar="config_path")
    parser.add_argument(
        "-t",
        "--timeout",
        dest="timeout",
        help="set timeout minutes between scrapings",
        action="store",
        type=int,
        default=10
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )

    # only to remove dataclasses_sql debug logs
    from loguru import logger
    logger.remove()


def main(args):
    args = parse_args(args)
    setup_logging(args.loglevel)

    try:
        parse_config(args.config_path)
    except KeyError as e:
        _logger.error(f'Invalid config file. Missing key: {e}')
        return -1
    except Exception as e:
        _logger.error(f'Invalid config file: {e}')
        return -2
    
    try:
        while True:
            try:
                scrape_apartments(args.config_path)
            except Exception as e:
                _logger.error(f'Unhandled error during scraping process: {e}')

            _logger.info(f'Sleeping {args.timeout} minutes..')
            time.sleep(args.timeout * 60)
    except KeyboardInterrupt:
        _logger.info('Bye')

    return 0


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m homescraper.skeleton 42
    #
    run()
