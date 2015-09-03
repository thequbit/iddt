import sys
import time

import utils
from daemon import Daemon
from mongo import Mongo


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

        #self.stdin_path = '/dev/null'
        #self.stdout_path = '/dev/tty'
        #self.stderr_path = '/dev/tty'
        #self.pidfile_path = pidfile_path
        #self.pidfile_timeout = 5

        self._mongo = Mongo(uri, db, url_collection, documents_collection)

        self.sleep_time = sleep_time

    def run(self):
        self.do_work()

    def do_work(self):

        '''
        This function sits until it is told to exist by setting self._running to False

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
            while not url is None:
                logger.info("Scrape: {0}".format(url['url']))
                no_work_count = 0
                if utils.check_match(url, url['url']):
                    page_urls, bandwidth, time_taken = utils.get_page_urls(url)
                    for pu in page_urls:
                        if utils.check_match(url, pu['url']):
                            document = pu
                            if not self._mongo.check_document_exists(url, document, use_job=True): 
                                self._mongo.add_document(url, document)
                    self._mongo.set_url_scraped(url)
            
                url = self._mongo.get_url()
            
            ''' This loop does document typing '''
            document = self._mongo.get_document()
            while not document is None:
                no_work_count = 0
                logger.info('Type: {0}'.format(document['url']))
                if utils.check_match(document, document['url']):
                    doc_type, bad_url, bandwidth, time_taken, count = utils.type_document(document)
                    self._mongo.set_document_type(document, doc_type, bad_url, bandwidth, time_taken)
                document = self._mongo.get_document()

            if no_work_count is 10:
                #logger.info("No Work.")
                print("No Work.")
                time.sleep(1)
                no_work_count = 0
            else:
                no_work_count += 1

if __name__ == '__main__':

    #worker = Worker()
    #worker.do_work()

    pidfile_path = '/tmp/worker.pid'
    if len(sys.argv) == 3:
        pidfile_path = sys.argv[2]
    logger.info('PID File: {0}'.format(pidfile_path))
    #worker = Worker(pidfile_path)

    daemon = Worker(pidfile=pidfile_path)
    if len(sys.argv) >= 2:
        logger.info('{} {}'.format(sys.argv[0],sys.argv[1]))
 
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.status()
        else:
            print ("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        logger.warning('show cmd deamon usage')
        print ("Usage: {} start|stop|restart".format(sys.argv[0]))
        sys.exit(2)

    '''
    logger = logging.getLogger("DaemonLog")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler("testdaemon.log")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    '''

    r = runner.DaemonRunner(worker)
    #r.daemon_context.files_preserve=[handler.stream]
    r.do_action()
