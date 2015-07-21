import time
import requests
from bs4 import BeautifulSoup
import urlparse
import urllib2
from urllib2 import HTTPError
import magic
import tldextract

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

    response = requests.get(url)

    bandwidth = (len(response.headers) + len(response.text))

    soup = BeautifulSoup(response.text, 'html.parser')

    title = ''
    title_tag = soup.find_all('title')
    if not len(title_tag) is 0 and not title_tag[0].string is None:
        title = title_tag[0].string.strip()

    tag_types = [
        ('a','href'),
        ('img','src'),
        ('link','href'),
        ('object','data'),
        ('source','src'),
        ('script','src'),
        ('embed','src'),
        ('iframe','src'),
    ]

    for tag_type, verb in tag_types:
        tags = soup.find_all(tag_type)
        for tag in tags:
            text = ''
            if len(tag.contents) >= 1:
                if not tag.string is None:
                    text = tag.string.strip()
   
            if verb in tag.__dict__['attrs']:
                raw_url = tag[verb].encode('utf-8')
            else:
                continue

            full_url = urlparse.urljoin(url, raw_url)

            _url = {
                'url': full_url,
                'text': text,
                'source_title': title,
                'source_url': url
            }
            urls.append(_url)

    taken = time.time() - start

    return urls, bandwidth, taken

def type_document(document, try_count=5, sleep_time=0, try_header_size=1024, timeout=60):

    '''
    document = {
        'url': 'http://example.com/',
        #'text': 'Example.com - Example Website URL',
        #'source_title': '<root>',
        #'source_url': '<root>',
    }
    '''

    start = time.time()

    header_size = try_header_size
    count = 0
    document_type = None
    bandwidth = 0
    bad_url = False

    # we don't need the entire dict
    url = document['url'].replace(' ', '%20')

    while count < (try_count + 1):

        if sleep_time > 0:
            time.sleep(sleep_time)

        #if count is try_count:
        #    print "Configuring urllib2 to download entire URL ..."
        #    request = urllib2.Request(url)
        #else:
        try:
            header_size += try_header_size
            headers = {
                'Range': 'byte=0-%i' % header_size,
            }
            request = urllib2.Request(url, headers=headers)

            #print "Downloading:"
            #print "{0}".format(url)
            response = urllib2.urlopen(request, timeout=timeout)
            headers = response.info()
            payload = response.read(header_size)
            bandwidth += ( len(headers) + len(payload) )
            document_type = magic.from_buffer(payload, mime=True)
            if document_type is None:
                #print "\t\tDocument Type was None, downloading entire file ..."
                #print "\t\t{0}".format(url)
                request = urllib2.Request(url)
                response = urllib2.urlopen(request, timeout=timeout)
                headers = response.info()
                payload = response.read(header_size)
                bandwidth += ( len(headers) + len(payload) )
                document_type = magic.from_buffer(payload, mime=True)
            #print "\tDownload complete.  Type: {0}".format(document_type)
            #print url, document_type
            break

        except HTTPError as e:

            if '500' in str(e):        
                #print "\t500 Error, attempting to download entire file ..." 
                try:
                    request = urllib2.Request(url)
                    response = urllib2.urlopen(request, timeout=timeout)
                    headers = response.info()
                    payload = response.read(header_size)
                    bandwidth += ( len(headers) + len(payload) )
                    document_type = magic.from_buffer(payload, mime=True)
                    #print "\tPost 500 Error Download complete.  Type: {0}".format(document_type)
                    #print url, document_type
                except Exception as e:
                    #print "Error: "
                    #print "\t{0}".format(e)
                    document_type = None
                    bad_url = True

            elif '404' in str(e):

                # this is a weird case where some times sites link
                # to above the root ... we try and fix that here
                if '../' in url:
                    url = url.replace('../','',1)
                if count is try_count:
                    bad_url = True
                    break
        except Exception as e:
            # some unknwon error, abort
            #print "General non-http Exception while fetching URL: {0}".format(e)
            break

        count += 1
        
    taken = time.time() - start

    return document_type, bad_url, bandwidth, taken, count

