import sys
import time

from iddt.utils import check_match
from iddt.utils import type_document
from iddt.utils import get_page_urls
from iddt.daemon import Daemon
from iddt.mongo import Mongo

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("iddt.worker")


class Worker(Daemon):

    def __init__(self,
                 pidfile='/tmp/worker.pid',
                 uri='mongodb://localhost:27017/',
                 db="_bo",
                 url_collection='_urls',
                 documents_collection='_docs',
                 sleep_time=0.1):

        super(Worker, self).__init__(pidfile)
        self._mongo = Mongo(uri, db, url_collection, documents_collection)
        self.sleep_time = sleep_time
        self._callback = None
        self.bandwidth = 0

    def register_callback(self, callback):
        self._callback = callback

    def run(self):
        try:
            self.bandwidth = 0
            self.do_work()
        except Exception as e:
            print(str(e))
    def do_work(self):
        '''
        This function sits until it is told to exit by
        setting self._running to False

        1) try and get a url to scrape
            1a) check if it's an allowed domain
            1b) scrape it and get all of the URLs it links to
            1c) go through all found URLs
                1cI)   check if it's an allowed domain
                1cII)  check if document exists in the collection
                1cIII) add document at level + 1

        Note: we loop until there are no more URLs to scrape

        2) try and get a document to type
            2a) check if it's an allowed domain
            2b) Type the link
            2c) update URL with new type data

        Note: we loop until there are no more documents to type

        '''
        no_work_count = 0
        self._running = True
        while self._running:
            time.sleep(self.sleep_time)
            ''' This loop does page scraping '''
            url = self._mongo.get_url()
            while url is not None:
                logger.info("Scrape: {0}".format(url['url']))
                no_work_count = 0
                if check_match(url, url['url']):
                    page_urls, bandwidth, time_taken = get_page_urls(url)
                    self.bandwidth += bandwidth
                    for pu in page_urls:
                        if check_match(url, pu['url']):
                            document = pu
                            if not self._mongo.check_document_exists(
                                    url, document, use_job=True):
                                self._mongo.add_document(url, document)
                    self._mongo.set_url_scraped(url)
                url = self._mongo.get_url()
            ''' This loop does document typing '''
            document = self._mongo.get_document()
            while document is not None:
                no_work_count = 0
                logger.info('Type: {0}'.format(document['url']))
                if check_match(document, document['url']):
                    doc_type, bad_url, bandwidth, time_taken, count = \
                        type_document(document)
                    self.bandwidth += bandwidth
                    self._mongo.set_document_type(
                        document, doc_type, bad_url,
                        bandwidth, time_taken
                    )
                    if self._callback is not None:
                        self._callback(document)
                document = self._mongo.get_document()
            if no_work_count is 10:
                print("No Work.")
                time.sleep(1)
                no_work_count = 0
            else:
                no_work_count += 1

if __name__ == '__main__':
    pidfile_path = '/tmp/worker.pid'
    if len(sys.argv) == 3:
        pidfile_path = sys.argv[2]
    logger.info('PID File: {0}'.format(pidfile_path))
    daemon = Worker(pidfile=pidfile_path)
    if len(sys.argv) >= 2:
        logger.info('{} {}'.format(sys.argv[0], sys.argv[1]))
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.status()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        logger.warning('show cmd deamon usage')
        print("Usage: {} start|stop|restart".format(sys.argv[0]))
        sys.exit(2)
