Ballroom Competition Scraper
======================
This system is meant to gather data from websites such as O2CM about ballroom competitions for analyses of results and placements.

Make sure that you have the following packages installed:

* libpq-dev
* postgresql
* python3-tidylib

Make sure that you have the following python packages installed:

* urllib3
* pytidylib
* bs4
* pygresql

Additionally, you will need a database running with the configurations specified in src/config.json and the specified database loaded with the SQL files in src/db.

The repository is broken up into several packages:

* .
  * crawler.py
    * Script that creates threads that run the webparsing framework
* db
  * Accessors and objects for competition database objects
* test
  * unittest package for testing code in the repository
* util
* webparser
  * single-page parsers, and other webparsing framework code

To run the crawler, you simply would need to run:

    $ python3 crawler.py --numWorkers <number-of-threads> --configFile <config-file-path> http://results.o2cm.com