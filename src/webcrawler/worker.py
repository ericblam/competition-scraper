import pickle
import threading
import traceback

from webparser import parserfactory
from util.webutils import WebRequest, loadPage

"""
Function each worker calls to do scraping work
Returns True if finished, False otherwise
"""
def scrapeFromQueue(q, conn, config):
    task = q.get()

    try:
        # if there are "None" tasks in the queue, we are done
        if task is None:
            return True

        # get HTML
        htmlDOM = loadPage(task.request)

        # if no hint, need to create one
        if task.hint is None:
            task.hint = parserfactory.getParserHint(task.request)

        # determine how to parse HTML
        parser = parserfactory.ParserFactory(q, conn, config, task.hint)

        # parse HTML
        if parser is not None:
            parser.parse(htmlDOM, task.data)
    except:
        stacktraceText = traceback.format_exc()
        print(stacktraceText)
        conn.insert("crawler.error",
                    task=conn.escape_bytea(pickle.dumps(task)),
                    error_description=stacktraceText)

    q.task_done()

    return False

class WorkerThread(threading.Thread):

    def __init__(self, q, conn, config):
        super(WorkerThread, self).__init__()
        self.q = q
        self.conn = conn
        self.config = config
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            if scrapeFromQueue(self.q, self.conn, self.config):
                break

    def stop(self):
        self.stop_event.set()
