# iddt
Internet Document Discovery Tool

## What is it

https://github.com/thequbit/iddt

There are three parts of `iddt`

- Worker
- Dispatcher
- MongoDB

The worker is what does all of the hard lifting with the internet, and 
the dispatcher keep everyone in line.  You can have any many workers as
you're system will allow mongdb connections.  MongoDB is used as the
central cache to limit the amount of bandwidth needed to scrape target
URLs.

##How to use it

###Requirements

`iddt` uses MongoDB as a central cache while it is working.  You'll need to
install MongoDB to use `iddt`.

- Ubuntu

    $ sudo apt-get install mongodb

###Worker

You will probably want to run the worker ( or many workers ) as daemons.
This functionality is built into `iddt`.  use the following code as a 
starting point:

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
            
    if __name__ == '__main__':
        pidfile_path = '/tmp/worker.pid'
        if len(sys.argv) == 3:
            pidfile_path = sys.argv[2]
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


This will allow you to start, stop, and restart a worker daemon at the
command prompt.  If you are interested in using the worker NOT as a 
daemon, you can execute the same functionality ( note this function
is fully blocking ) by using the .run() function.

    from iddt import Worker
    
    def new_doc(document):
        # do something with the document
        pass
    
    worker = MyWorker()
    worker.register_callback(new_doc)
    worker.run()

You're on your own to gracefully exit the `run()` function.  If you set
`worker._running` to `False` it *should* gracefully exit after a short while.

##Dispatcher

The dispatcher tells the workers what to work on.  You use it something like
this:

    from iddt.dispatcher import Dispatcher

    d = Dispatcher()
    d.dispatch({
        'target_url': 'http://example.com/',
        'link_level': 1,
        'allowed_domains': [],
    })

    # this is how you query the results based on mime type
    some_docs = dispatcher.get_documents(['application/pdf'])

    # this is how you get ALL of the documents
    all_docs = dispatcher.get_documents()

Note that the `dispatcher.dispatch()` function requires a dict with the 
following fields:

- `target_url`
    - This is the URL that the Workers (scrapers) should be working on
- `link_level`
    - This is the number of links to follow.  Be careful with numbers above 3
- `allowed_domains`
    - The `iddt` Worker won't follow links away from the TLD of the 
      `target_url`.  If you would like it to, you can supply the list of
      allowed domains here.

## Caution

This is a really powerful tool.  Please be curtious with it.
