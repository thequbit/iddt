# iddt
Internet Document Discovery Tool

https://github.com/thequbit/iddt

There are two parts of `iddt`: The Worker and the Dispatcher.  The worker
is what does all of the hard lifting with the internet, and the dispatcher
keep everyone in line.  You can have any many workers as you're system 
will allow mongdb connections.

###Worker

You will probably want to run the worker ( or many workers ) as daemons.
This functionality is built into `iddt`.  use the following code as a 
starting point:

    import sys
    from iddt import Worker

    class MyWorker(Worker):

        def __init__(self, *args, **kwargs):
            super(MyWorker, self).__init__( *args, **kwargs)

    if __name__ == '__main__':
        pidfile = '/tmp/worker.pid'
        if len(sys.argv) == 3:
            pidfile = sys.argv[2]
        worker = MyWorker(pidfile=pidfile)
        if len(sys.argv) >= 2:
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
            print("Usage: {} start|stop|restart".format(sys.argv[0]))
            sys.exit(2)

This will allow you to start, stop, and restart a worker daemon at the
command prompt.  If you are interested in using the worker NOT as a 
daemon, you can execute the same functionality ( note this function
is fully blocking ) by using the .run() function.

    from iddt import Worker
    
    worker = Worker()
    worker.run()

You're on your own to gracefully exit the `run()` function.  If you set
`worker._running` to `False` it *should* gracefully exit after a short while.

##Dispatcher

The dispatcher tells the workers what to work on.  You use it something like
this:

    from iddt import Dispatcher

    dispatcher = Dispatcher()

    # this will block until complete
    dispatcher.dispatch({
        'target_url': 'http://example.com',
        'link_level': 3,
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
