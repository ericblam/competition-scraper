Ballroom Competition Scraper
======================
This system is meant to gather data from websites such as O2CM about ballroom competitions for analyses of results and placements.

This repo uses Python 3.

To use o2cmScraper.py to scrape all competitions O2CM has:

    $ python3 o2cmScraper.py

To use o2cmScraper.py to scrape specific competitions:

    $ python3 o2cmScraper.py compId1 compId2 ...

For more help using o2cmScraper.py:

    $ python3 o2cmScraper.py --help

Additionally, competitionResults.py can be used to navigate the data or calculate [YCN](http://ballroom.mit.edu/index.php/ycn-proficiency-points/) points for an individual.