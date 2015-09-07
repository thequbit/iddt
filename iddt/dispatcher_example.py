from iddt.dispatcher import Dispatcher


class MyDispatcher(Dispatcher):

    def __init__(self):
        super(MyDispatcher, self).__init__()

d = MyDispatcher()
d.dispatch({
    'target_url': 'http://example.com',
    'link_level': 0,
    'allowed_domains': [],
})
