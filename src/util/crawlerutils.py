class ScraperTask:

    """
    Object containing information on what to scrape next.

    :param request: webUtils.WebRequest representing what page to fetch
    :param data: multi-level data from previous layer
    :param hint: hint for what kind of parser to use
    """
    def __init__(self, request, data = None, hint = None):
        self.request = request
        self.data = data
        self.hint = hint

    def __str__(self):
        return '%s\ndata: %s' % (self.request, self.data)
