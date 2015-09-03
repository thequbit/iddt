from pymongo import MongoClient
import datetime

class Mongo(object):

    '''
    Provides access to the mongodb instance
    '''

    def __init__(self,
                 uri='mongodb://localhost:27017/',
                 db="_bo",
                 url_collection='_urls',
                 documents_collection='_docs'):

        self._dbclient = MongoClient(uri)
        self._db = self._dbclient[db]
        self._urls = self._db[url_collection]
        self._documents = self._db[documents_collection]

        #self._urls.remove()
        #self._documents.remove()
        #raise Exception('debug')

    def get_counts(self, job):

        url_scraped_count = self._urls.find({'scraped': True, 'job': job}).count()
        url_not_scraped_count = self._urls.find({'scraped': False, 'job': job}).count()

        document_typed_count = self._documents.find({'typed': True, 'job': job}).count()
        document_not_typed_count = self._documents.find({'typed': False, 'job': job}).count()

        return url_scraped_count, url_not_scraped_count, document_typed_count, document_not_typed_count

    def add_url(self, url):
        '''
        Adds a URL to the list of URLs.

        Required:
            target_url:        The top of the URL pyramid, the target that started the job.
            job:               The unique job ID
            allowed_domains:   List of allowed domains other than the `url` domain.
            source_url:        The URL that linked to this URL
            source_title:      The Title of the HTML page of the `source_url`
            text:              The text in the link that linked to this URL
            url:               The URL to be scraped
            level:             The link level this URL exists at

        Adds:
            creation_datetime: The datetime when the URL was added to the collection
            scraped:           Boolean to detrumine if the URL has been scraped
            in_process:        Used as semaphore in conjunction with find_and_modify()
            
        '''
        reqkeys = [
            'target_url',
            'job',
            'allowed_domains',
            #'source_url',
            #'source_title',
            #'text',
            'url',
            'level',
        ]
        for key in reqkeys:
            if not key in url:
                raise Exception("URL is Missing Required Key: %s" % key)
        url['creation_datetime'] = datetime.datetime.now()
        url['scraped'] = False
        url['in_progress'] = False
        self._urls.insert(url)
        #print "add_url(): added:"
        #print url

    def check_url_exists(self, url):
        '''
        Sees if the URL (for this job) already exists within the collection.
        '''
        response = self._urls.find_one({'url': url['url'], 'job': url['job']})
        exists = False
        if not response is None:
            exists = True
        return exists

    def get_url(self):
        '''
        Gets a URL from the list of URLs, and removes it from the collection.

        Sets in_progress semaphore to prevent being scraped more than once.
        '''
        url = self._urls.find_one()
        url = self._urls.find_and_modify(
            {'scraped': False, 'in_progress': False},
            update={'$set': {'in_progress': True}},
            multi=False,
        )
        return url

    def set_url_scraped(self, url):
        '''
        Sets the URL to scraped.
        '''
        if 'in_progress' in url:
            del(url['in_progress'])
        url['scraped'] = True
        url['scraped_datetime'] = datetime.datetime.now()
        self._urls.update({'_id': url['_id']}, url)

    def add_document(self, url, document):
        '''
        Adds a document to the list of documents.

        Required in Document:
            url:               The URL to be scraped

        Required in URL:
            target_url:        The top of the URL pyramid, the target that started the job.
            job:               The unique job ID
            allowed_domains:   List of allowed domains other than the `url` domain.
            source_url:        The URL that linked to this URL
            source_title:      The Title of the HTML page of the `source_url`
            text:              The text in the link that linked to this URL
            level:             The link level this URL exists at

        Adds the following fields:
            creation_datetime: The datetime when the URL was added to the collection
            typed:             Boolean to be set once document URL is typed
            being_typed:       used as a semaphore in conjunction with find_and_modify()
            
        '''
        if not 'url' in document:
            raise Exception("Document is Missing Required Key: url")
        reqkeys = [
            'target_url',
            'job',
            'allowed_domains',
            # these come from document
            #'source_url',
            #'source_title',
            #'text',
            'level',
        ]
        for key in reqkeys:
            if not key in url:
                raise Exception("URL is Missing Required Key: %s" % key)
            document[key] = url[key]
        document['creation_datetime'] = datetime.datetime.now()
        document['typed'] = False
        document['being_typed'] = False
        document['level'] = url['level'] + 1 # need to bump to next level
        self._documents.insert(document)

    def check_document_exists(self, url, document, use_job=False):
        '''
        Checks to see if the document already exists in the collection.
        '''
        query = {'url': document['url']}
        if use_job:
            query['job'] = url['job']
        response = self._documents.find_one(query)
        exists = False
        if not response is None:
            exists = True
        return exists


    def get_document(self):
        '''
        Gets a document from the list of documents to be typed

        Sets being_typed semaphore to prevent being typed more than once.
        '''
        
        doc = self._documents.find_and_modify(
            {'typed': False, 'being_typed': False},
            {'being_typed': True},
            multi=False,
        )
        return doc

    def set_document_type(self, document, doc_type, bad_url, bandwidth, time_taken):
        '''
        Sets the document type.
        '''
        if 'being_typed' in document:
            del(document['being_typed'])
        document['doc_type'] = doc_type
        document['bad_url'] = bad_url
        document['bandwidth'] = bandwidth
        document['time_taken'] = time_taken
        document['typed'] = True
        document['typed_datetime'] = datetime.datetime.now()
        self._documents.update({'_id': document['_id']}, document)

    def get_documents_at_level(self, job, level):
        '''
        Gets all of the HTTL URLs at the specific level
        '''
        docs = self._documents.find({
            'job': job,
            'level': level,
            'typed': True,
            #'doc_type': 'text/html',
        })
        #print "get_documents_at_level(), level: {0}, job: {1}, len(docs): {2}".format(level, job, docs.count())
        return docs

    def set_document_contents(self, url, contents):
        '''
        Sets the document's contents.
        '''
        url['contents'] = contents
        url['contents_datetime'] = datetime.datetime.now()
        self._documents.update({'_id': url['_id']}, url)

    def get_all_documents(self, job):
        '''
        Gets all of the documents for the job
        '''

        documents = []
        docs = self._documents.find({'job': job})
        for doc in docs:
            for key in doc:
                if '_id' in key or 'datetime' in key:
                    doc[key] = str(doc[key])
            documents.append(doc)

        return documents

    def get_documents(self, job, doc_type):
        '''
        Gets all of the documents for the job of specific document mime type
        '''

        documents = []
        docs = self._documents.find({'job': job, 'doc_type': doc_type})
        for doc in docs:
            for key in doc:
                if '_id' in key or 'datetime' in key:
                    doc[key] = str(doc[key])
            documents.append(doc)

        return documents

    def log_error(self, job, url, error_text):
        '''
        Logs an error with a job
        '''
        error = dict(
            job = job,
            datetime = str(datetime.datetime.now()),
            url = url,
            error_text = error_text,
        )
        self._errors.insert(error)

    def get_errors(self, job):
        '''
        Gets all of the errors for a specific job
        '''
        errors = self._errors.find({'job': job})
        return errors

if __name__ == '__main__':

    uri='mongodb://localhost:27017/'
    db="_bo"
    url_collection='_urls'
    documents_collection='_docs'

    _dbclient = MongoClient(uri)
    _db = _dbclient[db]
    _urls = _db[url_collection]
    _documents = _db[documents_collection]

    _urls.remove()
    _documents.remove()

