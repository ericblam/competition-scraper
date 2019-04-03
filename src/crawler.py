import argparse
import queue

from abc import ABC, abstractmethod
from enum import Enum
from util.webUtils import getHostname

class SiteMetadata:

    def __init__(self, url, data = None, hint = None):
        self.url = url
        self.data = data
        self.hint = hint

    def getUrl(self):
        return self.url

    def getData(self):
        return self.data

    def getHint(self):
        return self.hint

class CrawlerType(Enum):
    O2CM = 1
    COMPMNGR = 2

hostToCrawlerType = {
    "o2cm": CrawlerType.O2CM,
    "compmngr": CrawlerType.COMPMNGR
}

class Crawler(ABC):

    def __init__(self, q):
        self.queue = q

    @abstractmethod
    def scrape(self, siteMetadata):
        pass


def parseArgs():
    """
    Parses command-line arguments
    """

    parser = argparse.ArgumentParser(description="Crawl around a website to scrape")
    parser.add_argument(
        "seedUrl"
        , nargs = "+"
        , type  = str
        , help  = "first url to scrape for information"
    )
    parser.add_argument(
        "-d"
        , "--domain"
        , nargs = 1
        , type  = str
        , help  = "Main domain name of website to parse"
    )
    parser.add_argument(
        "-n"
        , "--numCrawlers"
        , nargs   = 1
        , type    = int
        , default = 4
        , help    = "Number of crawlers to spawn"
    )
    return parser.parse_args()

def CreateCrawler(t):
    if t == CrawlerType.O2CM:
        return t
    elif t == CrawlerType.COMPMNGR:
        return t

if __name__ == "__main__":

    args = parseArgs()

    host = ""
    if args.domain is not None:
        host = getHostname(args.domain)
    else:
        host = getHostname(args.seedUrl[0])

    q = queue.Queue()

    if host not in hostToCrawlerType:
        print("no crawlers available for '" + host + "'")
        exit()

    crawlers = []
    for i in range(args.numCrawlers):
        crawler = CreateCrawler(hostToCrawlerType[host])
        crawlers.append(crawler)

    # create threads for crawlers
    # allocate crawlers to threads appropriately
    # crawlers should scrape the front of the queue
    # once done crawlers should push any relevant data to the queue

    # TODO
