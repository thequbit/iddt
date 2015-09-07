import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import magic
import tldextract
import http.client


def check_match(_url, url):
    target_url = _url['target_url']
    allowed_domains = _url['allowed_domains']
    match = False
    url_domain = tldextract.extract(url).domain.lower()
    target_url_domain = tldextract.extract(target_url).domain.lower()
    if url_domain == target_url_domain or url_domain in allowed_domains:
        match = True
    return match


def get_page_urls(_url):
    '''
    url = 'http://example.com'
    '''
    start = time.time()
    url = _url['url']
    urls = []
    bandwidth = 0
    try:
        response = requests.get(url)
    except Exception as e:
        taken = time.time() - start
        return [], 0, taken
    bandwidth = (len(response.headers) + len(response.text))
    soup = BeautifulSoup(response.text, 'html.parser')
    title = ''
    title_tag = soup.find_all('title')
    if not len(title_tag) is 0 and not title_tag[0].string is None:
        title = title_tag[0].string.strip()
    tag_types = [
        ('a', 'href'),
        ('img', 'src'),
        ('link', 'href'),
        ('object', 'data'),
        ('source', 'src'),
        ('script', 'src'),
        ('embed', 'src'),
        ('iframe', 'src'),
    ]
    for tag_type, verb in tag_types:
        tags = soup.find_all(tag_type)
        for tag in tags:
            link_text = ''
            if len(tag.contents) >= 1:
                if tag.string is not None:
                    link_text = tag.string.strip()
            raw_url = ''
            if verb in tag.__dict__['attrs']:
                raw_url = tag[verb]
            else:
                continue
            full_url = urljoin(url, raw_url)
            new_url = {
                'url': full_url,
                'link_text': link_text,
                'source_url_title': title,
                'source_url': url
            }
            urls.append(new_url)
    taken = time.time() - start
    return urls, bandwidth, taken


def type_document(document, try_count=5, sleep_time=0,
                  header_size=1024, timeout=60):
    '''
    document = {
        'url': 'http://example.com/',
        #'text': 'Example.com - Example Website URL',
        #'source_title': '<root>',
        #'source_url': '<root>',
    }
    '''
    start = time.time()
    count = 0
    document_type = None
    bandwidth = 0
    bad_url = False
    # we don't need the entire dict
    url = document['url'].replace(' ', '%20')
    while count < (try_count + 1):
        if sleep_time > 0:
            time.sleep(sleep_time)
        try:
            resp = requests.get(
                url, headers={'Range': 'bytes=0-%i' % header_size}, stream=True
            )
            payload = resp.content
            # TODO: include full transaction bandwidth, not just response
            #       we could be off by quite a bit here.
            bandwidth += len(payload)
            document_type = magic.from_buffer(
                payload, mime=True,
            ).decode('ascii')
            if document_type is None:
                resp = requests.get(url, stream=True)
                payload = resp.content
                # TODO: include full transaction bandwidth, not just response
                #       we could be off by quite a bit here.
                bandwidth += len(payload)
                document_type = magic.from_buffer(
                    payload, mime=True,
                ).decode('ascii')
            break
        except:
            count += 1
    taken = time.time() - start
    return document_type, bad_url, bandwidth, taken, count
