import os
import urllib.error, urllib.parse, urllib.request
from bs4 import BeautifulSoup
from tidylib import tidy_document

CACHE_DIR = os.path.dirname(__file__) + "/../.cache/"

class WebRequest(object):

    def __init__(self, url, requestType="GET", data={}):
        self.url = url
        self.requestType = requestType
        self.data = data
        self.forceReload = False

    def __str__(self):
        return "Request to %s (%s); %s" % (self.url, self.requestType, self.data)


def loadPage(requestObj):
    """
    Loads a page from a url with data
    """

    url = requestObj.url
    data = requestObj.data
    requestType = requestObj.requestType
    forceReload = requestObj.forceReload

    request = urllib.parse.urlencode(data)

    sortedDataString = "_".join([str(i) + "=" + str(data[i]) for i in sorted(data.keys())])
    cacheFilename = url
    if (len(sortedDataString) > 0):
        cacheFilename += "_" + requestType + "_" + sortedDataString

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
        if requestType == "GET":
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

def getHostname(url):
    if not url.startswith("http://") or not url.startswith("https://"):
        url = "http://" + url
    fullhost = urllib.parse.urlparse(url).hostname
    if fullhost.count(".") >= 1:
        return ".".join(fullhost.split(".")[-2:-1])
    return fullhost
