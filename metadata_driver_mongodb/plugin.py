import logging

from metadatadb_driver_interface.plugin import AbstractPlugin
from metadatadb_driver_interface.search_model import FullTextModel, QueryModel
from pymongo import DESCENDING

from metadata_driver_mongodb.instance import get_database_instance
from metadata_driver_mongodb.utils import query_parser

logger = logging.getLogger(__name__)


class Plugin(AbstractPlugin):
    """Mongo ledger plugin for `Metadata DB's Python reference
    implementation <https://github.com/nevermined-io/metadata-driver-mongodb>`_.
    Plugs in a MongoDB instance as the persistence layer for Metadata Db
    related actions.
    """

    def __init__(self, config=None):
        """Initialize a :class:`~.Plugin` instance and connect to MongoDB.
        Args:
            *nodes (str): One or more URLs of MongoDB nodes to
                connect to as the persistence layer
        """
        self.driver = get_database_instance(config)
        self.logger = logging.getLogger('Plugin')
        logging.basicConfig(level=logging.INFO)

    @property
    def type(self):
        """str: the type of this plugin (``'MongoDB'``)"""
        return 'MongoDB'

    @staticmethod
    def _num_to_skip(page, num_per_page):
        return (page - 1) * num_per_page

    def write(self, obj, resource_id=None):
        if resource_id is not None:
            obj['_id'] = resource_id
        o = self.driver.instance.insert_one(obj)
        self.logger.debug('mongo::write::{}'.format(o.inserted_id))
        return o.inserted_id

    def read(self, resource_id):
        return self.driver.instance.find_one({"_id": resource_id})

    def update(self, obj, resource_id):
        prev = self.read(resource_id)
        self.logger.debug('mongo::update::{}'.format(resource_id))
        return self.driver.instance.replace_one(prev, obj)

    def delete(self, resource_id):
        self.logger.debug('mongo::delete::{}'.format(resource_id))
        return self.driver.instance.delete_one({"_id": resource_id})

    def list(self, search_from=None, search_to=None, limit=0):
        return self.driver.instance.find().limit(limit)

    def query(self, search_model: QueryModel):
        assert search_model.page >= 1, 'page value %s is invalid' % search_model.page

        query_result = self.driver.instance.find(query_parser(search_model.query))
        sort_params = [('service.metadata.curation.rating', DESCENDING)]
        if search_model.sort is not None:
            sort_params = list(search_model.sort.items())

        return (
            query_result.sort(sort_params)
            .skip(self._num_to_skip(search_model.page, search_model.offset))
            .limit(search_model.offset),
            query_result.count()
        )

    def text_query(self, full_text_model: FullTextModel):
        assert full_text_model.page >= 1, 'page value %s is invalid' % full_text_model.page

        find_params = {"score": {"$meta": "textScore"}}

        if full_text_model.sort is None:
            sort_params = [
                ('score', {'$meta': 'textScore'}),
                ('service.metadata.curation.rating', DESCENDING)]
        else:
            sort_params = list(full_text_model.sort.items())

        query_result = self.driver.instance.find(
            {"$text": {"$search": full_text_model.text}},
            find_params
        )

        return (
            query_result.sort(sort_params)
            .skip(self._num_to_skip(full_text_model.page, full_text_model.offset))
            .limit(full_text_model.offset),
            query_result.count()
        )
