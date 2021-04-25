import datetime
import logging
import pickle
import threading
import traceback

from webparser import parserfactory
from util.dbutils import createConnFromConfig
from util.logutils import LogTimer
from util.webutils import WebRequest, loadPage

"""
Function each worker calls to do scraping work
Returns True if finished, False otherwise
"""
def scrapeFromQueue(q, config):
    task = q.get()

    try:
        # if there are "None" tasks in the queue, we are done
        if task is None:
            return True

        # get HTML
        with LogTimer("Loading and DOMing page"):
            htmlDOM = loadPage(task.request)

        # if no hint, need to create one
        if task.hint is None:
            task.hint = parserfactory.getParserHint(task.request)

        # determine how to parse HTML
        parser = parserfactory.ParserFactory(q, config, task.hint)

        # parse HTML
        if parser is not None:
            with LogTimer("Parsing page ({})".format(str(task))):
                parser.parse(htmlDOM, task.data)
    except:
        stacktraceText = traceback.format_exc()
        logging.error(stacktraceText)
        with createConnFromConfig(config) as conn, conn.cursor() as cursor:
            cursor.execute('INSERT INTO crawler.error (task, error_description) VALUES (%s, %s)', (pickle.dumps(task), stacktraceText)) # TODO: Verify this works after converting to psycopg2. May need to escape_bytea

    q.task_done()

    return False

class WorkerThread(threading.Thread):

    def __init__(self, q, config):
        super(WorkerThread, self).__init__()
        self.q = q
        self.config = config
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            if scrapeFromQueue(self.q, self.config):
                break

    def stop(self):
        self.stop_event.set()
