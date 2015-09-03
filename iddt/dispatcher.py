import sys
import time
import datetime
import uuid
import json

from mongo import Mongo

import logging.basicConfig(level=loggin.INFO)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("iddt.dispatcher")


class Dispatcher(object):

    def __init__(self,
                 uri='mongodb://localhost:27017/',
                 db="_bo",
                 url_collection='_urls',
                 documents_collection='_docs'):

        self._mongo = Mongo(uri, db, url_collection, documents_collection)
        self.reset()

    def reset(self):
        self.job = '{0}-{1}'.format(str(uuid.uuid4()), str(uuid.uuid4()))

    def add_url(self, url):
        url['text'] = '<root>'
        url['job'] = self.job
        url['url'] = url['target_url']
        url['level'] = 0
        self._mongo.add_url(url)

    def load_urls_at_level(self, level):
        documents = self._mongo.get_documents_at_level(self.job, level)
        url_count = 0
        for doc in documents:
            if '_id' in doc:
                del(doc['_id'])
            keys = [
                'target_url',
                'job',
                'allowed_domains',
                'url',
                'level',
            ]
            url = {}
            for key in keys:
                url[key] = doc[key]
            self._mongo.add_url(url)
            url_count += 1
        return url_count

    def dispatch(self, url):
        '''
        Dispatches the URLs to the workers

        url = {
            'target_url': '',
            'link_level': 0,
            'allowed_domains': [],
        }
        '''
        reqkeys = [
            'target_url',
            'link_level',
            'allowed_domains',
        ]
        for key in reqkeys:
            if key not in url:
                raise Exception('Missing key in URL: %s' % key)

        self.add_url(url)

        link_level = url['link_level']
        level = 0
        while level < link_level+1:
            url_count = self.load_urls_at_level(level)
            working = True
            while working:
                scraped, not_scraped, typed, not_typed = self._mongo.get_counts(self.job)
                if not_scraped is 0 and not_typed is 0:
                    working = False
                else:
                    time.sleep(1)
                logger.info("Level: {0} / {1}, Not Scraped: {2}, Not Typed: {3}".format(level, link_level, not_scraped, not_typed))
            level += 1

        print("All URLs processed.")

    def get_documents(self, doc_types=['*']):
        docs = []
        for doc_type in doc_types:
            print("doc type: {0}".format(doc_type))
            if doc_type == "*":
                docs = self._mongo.get_all_documents(self.job)
                break
            else:
                for doc in self._mongo.get_documents(self.job, doc_type):
                    docs.append(doc)
        return docs

"""
if __name__ == '__main__':

    dispatcher = Dispatcher()
    documents = dispatcher.dispatch({'target_url': 'http://www.townofchili.org/', 'link_level': 3, 'allowed_domains': []})
    #dispatcher.dispatch({'target_url': 'http://timduffy.me/', 'link_level': 5, 'allowed_domains': []})
    #print(documents)
    documents = dispatcher.get_documents(['application/pdf'])
    with open('docs.json', 'w') as f:
        f.write(json.dumps(documents))
    print("Discovered {0} documents.".format(len(documents)))
"""
