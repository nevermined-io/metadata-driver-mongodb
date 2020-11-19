from ssl import CERT_NONE, CERT_REQUIRED

from metadatadb_driver_interface.utils import get_value
from pymongo import MongoClient, TEXT

from metadata_driver_mongodb.indexes import list_indexes

_DB_INSTANCE = None


def get_database_instance(config_file=None):
    global _DB_INSTANCE
    if _DB_INSTANCE is None:
        _DB_INSTANCE = MongoInstance(config_file)

    return _DB_INSTANCE


class MongoInstance(object):

    def __init__(self, config=None):
        host = get_value('db.hostname', 'DB_HOSTNAME', 'localhost', config)
        port = int(get_value('db.port', 'DB_PORT', 27017, config))
        db_name = get_value('db.name', 'DB_NAME', 'db_name', config)
        collection = get_value('db.collection', 'DB_COLLECTION', 'collection_name', config)
        username = get_value('db.username', 'DB_USERNAME', None, config)
        password = get_value('db.password', 'DB_PASSWORD', None, config)

        ssl = get_value('db.ssl', 'DB_SSL', 'false', config)
        verify_certs = get_value('db.verify_certs', 'DB_VERIFY_CERTS', 'false', config)
        if verify_certs is False:
            ssl_cert_reqs = CERT_NONE
        else:
            ssl_cert_reqs = CERT_REQUIRED

        ca_cert_path = get_value('db.ca_cert_path', 'DB_CA_CERTS', None, config)
        client_key = get_value('db.client_key', 'DB_CLIENT_KEY', None, config)
        client_cert_path = get_value('db.client_cert_path', 'DB_CLIENT_CERT', None, config)

        if ssl == 'true':
            self._client = MongoClient(host=host,
                                       port=port,
                                       ssl=ssl,
                                       ssl_cert_reqs=ssl_cert_reqs,
                                       ssl_ca_certs=ca_cert_path,
                                       ssl_certfile=client_cert_path,
                                       ssl_keyfile=client_key)
        else:
            self._client = MongoClient(host=host,
                                       port=port
                                       )
        self._db = self._client[db_name]
        if username is not None and password is not None:
            print('username/password: %s, %s' % (username, password))
            self._db.authenticate(name=username, password=password)

        self._collection = self._db[collection]
        self._collection.create_index([("$**", TEXT)])
        for index in list_indexes:
            self._collection.create_index(index)

    @property
    def instance(self):
        return self._collection
