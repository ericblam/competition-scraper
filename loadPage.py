import urllib.error, urllib.parse, urllib.request
from bs4 import BeautifulSoup
from tidylib import tidy_document

"""
Loads a page from a url with data (uses GET if !post, else uses POST)
"""
def loadPage(url, data={}, post=False):
    request = urllib.parse.urlencode(data)
    try:
        if (not post):
            getUrl = url + ('?' if len(data) != 0 else '') + request
            response = urllib.request.urlopen(getUrl)
        else:
            response = urllib.request.urlopen(url, request.encode('ascii'))
        html_response = response.read()
        encoding = response.headers.get_content_charset('utf-8')
        decoded_html = html_response.decode(encoding)
        tidiedPage, pageErrors = tidy_document(decoded_html)
        return BeautifulSoup(tidiedPage, 'html.parser')
    except urllib.error.HTTPError:
        print("Failed to fetch %s with request: %s" % (url, request))
        return None
    # return BeautifulSoup(u, 'html.parser')
