import argparse
import logging
import signal

from util.comp_utils import *
from util.loadPage import loadPage
from db.dbObjects import *
from db.dbAccessor import *

LOG_FILE_NAME = ".o2cmScraper.log"

def main():
    initialize()

def initialize():
    parser = argparse.ArgumentParser(description="Scrape O2CM database")
    parser.add_argument("comps",
                        nargs="*",
                        help="competition ids from which to scrape")
    parser.add_argument("--clear",
                        dest="clear",
                        nargs=1,
                        default=None,
                        help="clears data from specified competition")
    parser.add_argument("--reset",
                        dest="reset",
                        action='store_true',
                        default=False,
                        help='resets database')
    parser.add_argument("--verbose",
                        dest="verbose",
                        action='store_true',
                        default=False,
                        help='Outputs verbosely')
    args = parser.parse_args()

    # Open Log
    logLevel = logging.DEBUG
    if (args.verbose):
        logLevel = logging.INFO
    logging.basicConfig(filename=LOG_FILE_NAME,
                        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                        datefmt="%y-%m-%d %H:%M:%S",
                        level=logLevel)


    signal.signal(signal.SIGINT, sigintHandler)

    # reset database if appropriate
    if (args.reset):
        dbReset()

    if (args.clear is not None):
        dbClearComp(args.clear[0])
        exit(0)


if __name__ == "__main__":
    main()
