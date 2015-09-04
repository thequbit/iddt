import sys
from iddt import Worker

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("iddt.worker_test")

class MyWorker(Worker):

    def __init__(self, *args, **kwargs):
        super(MyWorker, self).__init__()
        logging.info("MyWorker __init__() complete.")

    def new_doc(self, document):
        # do something with the document
        pass 

#worker = MyWorker()
#worker.register_callback(worker.new_doc)
#worker.run()


if __name__ == '__main__':
    pidfile_path = '/tmp/worker.pid'
    if len(sys.argv) == 3:
        pidfile_path = sys.argv[2]
    #logger.info('PID File: {0}'.format(pidfile_path))
    worker = MyWorker(pidfile=pidfile_path)
    worker.register_callback(worker.new_doc)
    if len(sys.argv) >= 2:
        #logger.info('{} {}'.format(sys.argv[0], sys.argv[1]))
        if 'start' == sys.argv[1]:
            worker.start()
        elif 'stop' == sys.argv[1]:
            worker.stop()
        elif 'restart' == sys.argv[1]:
            worker.restart()
        elif 'status' == sys.argv[1]:
            worker.status()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        #logger.warning('show cmd deamon usage')
        print("Usage: {} start|stop|restart".format(sys.argv[0]))
        sys.exit(2)

