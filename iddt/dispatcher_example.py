from iddt.dispatcher import Dispatcher

d = Dispatcher()
d.dispatch({
    'target_url': 'http://timduffy.me/',
    'link_level': 3,
    'allowed_domains': [],
})

