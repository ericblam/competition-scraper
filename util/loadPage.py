import os
import urllib.error, urllib.parse, urllib.request
from bs4 import BeautifulSoup
from tidylib import tidy_document

CACHE_DIR = os.path.dirname(__file__) + "/../.cache/"

def loadPage(url, data={}, post=False, forceReload=False):
    """
    Loads a page from a url with data (uses GET if !post, else uses POST)
    """

    request = urllib.parse.urlencode(data)

    sortedDataString = "_".join([str(i) + "=" + str(data[i]) for i in sorted(data.keys())])
    cacheFilename = url
    if (len(sortedDataString) > 0):
        cacheFilename += "_" + ("POST" if post else "GET") + "_" + sortedDataString

    cacheFilename = cacheFilename.replace("https://","").replace("http://", "").replace("/", "_")
    if (not os.path.exists(CACHE_DIR)):
        os.makedirs(CACHE_DIR)

    cacheFilename = CACHE_DIR + cacheFilename
    if (not forceReload and os.path.exists(cacheFilename)):
        cachedPage = open(cacheFilename)
        tidiedPage = cachedPage.read()
        cachedPage.close()
        return BeautifulSoup(tidiedPage, "html.parser")

    try:
        if (not post):
            getUrl = url + ("?" if len(data) != 0 else "") + request
            response = urllib.request.urlopen(getUrl)
        else:
            response = urllib.request.urlopen(url, request.encode("ascii"))
        html_response = response.read()
        encoding = response.headers.get_content_charset("utf-8")
        decoded_html = html_response.decode(encoding)
        tidiedPage, pageErrors = tidy_document(decoded_html)

        cachedPage = open(cacheFilename, "w+")
        cachedPage.write(tidiedPage)
        cachedPage.close()

        return BeautifulSoup(tidiedPage, "html.parser")
    except urllib.error.HTTPError:
        print("Failed to fetch %s with request: %s" % (url, request))
        return None
    # return BeautifulSoup(u, "html.parser")
