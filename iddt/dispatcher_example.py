from iddt.dispatcher import Dispatcher

d = Dispatcher()
d.dispatch({
    'target_url': 'http://example.com/',
    'link_level': 1,
    'allowed_domains': [],
})

