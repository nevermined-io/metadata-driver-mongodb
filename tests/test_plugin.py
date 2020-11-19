from datetime import datetime, timedelta

import pytest
from metadatadb_driver_interface.metadatadb import MetadataDb
from metadatadb_driver_interface.search_model import FullTextModel, QueryModel

from metadata_driver_mongodb.utils import query_parser
from .ddo_example import ddo_sample

mongo = MetadataDb('./tests/config.ini').plugin


def test_plugin_type_is_mongodb():
    assert mongo.type == 'MongoDB'


def test_plugin_write_and_read():
    did = 'did:ocn-asset:0x123456789abcdefghi#path1'
    mongo.write({'value': 'test'}, did)
    assert mongo.read(did)['_id'] == did
    assert mongo.read(did)['value'] == 'test'
    mongo.delete(did)


def test_update():
    mongo.write({'value': 'test'}, 1)
    assert mongo.read(1)['value'] == 'test'
    mongo.update({'value': 'testUpdated'}, 1)
    assert mongo.read(1)['value'] == 'testUpdated'
    mongo.delete(1)


def test_plugin_list():
    mongo.write({'value': 'test1'}, 1)
    mongo.write({'value': 'test2'}, 2)
    mongo.write({'value': 'test3'}, 3)
    assert mongo.list().count() == 3
    assert mongo.list()[0]['value'] == 'test1'
    mongo.delete(1)
    mongo.delete(2)
    mongo.delete(3)


# def test_plugin_query():
#     mongo.write(ddo_sample, ddo_sample['id'])
#     search_model = QueryModel({'price': [0, 12]})
#     assert mongo.query(search_model)[0][0]['id'] == ddo_sample['id']
#     search_model_2 = QueryModel({'price': [0, 12], 'license': ['CC-BY']})
#     assert mongo.query(search_model_2)[0][0]['id'] == ddo_sample['id']
#     search_model_3 = QueryModel(
#         {'price': [0, 12], 'license': ['CC-BY'], 'type': ['Access', 'Metadata']})
#     assert mongo.query(search_model_3)[0][0]['id'] == ddo_sample['id']
#     search_model_4 = QueryModel({'sample': []})
#     assert mongo.query(search_model_4)[0][0]['id'] == ddo_sample['id']
#     search_model_5 = QueryModel({'created': ['today']})
#     assert mongo.query(search_model_5)[0].retrieved == 0
#     search_model_6 = QueryModel({'created': []})
#     assert mongo.query(search_model_6)[0][0]['id'] == ddo_sample['id']
#     search_model_7 = QueryModel({'text': ['weather']})
#     assert mongo.query(search_model_7)[0][0]['id'] == ddo_sample['id']
#     search_model_8 = QueryModel({'text': ['weather'], 'price': [0, 12]})
#     assert mongo.query(search_model_8)[0][0]['id'] == ddo_sample['id']
#     mongo.delete(ddo_sample['id'])
#
#
# def test_plugin_query_text():
#     total = 15
#     mongo.write({'key': 'A', 'value': 'test first'}, 1)
#     mongo.write({'key': 'B', 'value': 'test second'}, 2)
#     mongo.write({'key': 'C', 'value': 'test third'}, 3)
#     mongo.write({'key': 'D', 'value': 'test fourth'}, 4)
#     search_model = FullTextModel('test', {'key': -1}, offset=3, page=1)
#     search_model1 = FullTextModel('test', {'key': -1}, offset=3, page=2)
#     assert mongo.text_query(search_model)[0].count(with_limit_and_skip=True) == 3
#     assert mongo.text_query(FullTextModel('test'))[0].count(with_limit_and_skip=True) == 4
#     assert mongo.text_query(search_model)[0][0]['key'] == 'D'
#     assert mongo.text_query(search_model)[0][1]['key'] == 'C'
#     assert mongo.text_query(search_model1)[0][0]['key'] == 'A'
#
#     for i in range(5, total+1):
#         value = 'test %s' % i
#         mongo.write({'key': str(i), 'value': value}, i)
#
#     offset = 4
#     for page in range(1, 4):  # page: 1, 2, 3
#         result = mongo.text_query(FullTextModel('test', offset=offset, page=page))
#         assert result[1] == total
#         assert result[0].count(with_limit_and_skip=True) == offset
#
#     result = mongo.text_query(FullTextModel('test', offset=offset, page=4))
#     assert result[0].count(with_limit_and_skip=True) == (total % offset)
#
#     # Clean up
#     for i in range(1, total):
#         mongo.delete(i)


def test_query_parser():
    query = {'price': [0, 10]}
    assert query_parser(query) == {"service.metadata.base.price": {"$gte": 0, "$lte": 10}}
    query = {'price': [15]}
    assert query_parser(query) == {"service.metadata.base.price": {"$gte": 0, "$lte": 15}}
    query = {'type': ['Access', 'Metadata']}
    assert query_parser(query) == {
        "$and": [{"service.type": "Access"}, {"service.type": "Metadata"}]}
    query = {'license': []}
    assert query_parser(query) == {}
    query = {'license': [], 'type': ['Access', 'Metadata']}
    assert query_parser(query) == {
        "$and": [{"service.type": "Access"}, {"service.type": "Metadata"}]}
    query = {'license': ['CC-BY'], 'type': ['Access', 'Metadata']}
    assert query_parser(query) == {"$or": [{"service.metadata.base.license": "CC-BY"}], "$and": [
        {"service.type": "Access"},
        {"service.type": "Metadata"}]}
    query = {'created': ['today', 'lastWeek', 'lastMonth', 'lastYear']}
    assert query_parser(query)['created']['$gte'].year == (datetime.now() - timedelta(days=365)).year
    query = {'created': ['no_valid']}
    assert query_parser(query)['created']['$gte'].year == (
        datetime.now() - timedelta(weeks=1000)).year
    query = {'categories': ['weather', 'other']}
    assert query_parser(query) == {"$or": [{"service.metadata.base.categories": "weather"},
                                           {"service.metadata.base.categories": "other"}]}
    query = {'text': ['weather']}
    assert query_parser(query) == {"$text": {"$search": "weather"}}


def test_query_not_supported():
    query = {'not_supported': []}
    with pytest.raises(Exception):
        query_parser(query)


# def test_default_sort():
#     mongo.write(ddo_sample, ddo_sample['id'])
#     ddo_sample2 = ddo_sample.copy()
#     ddo_sample2['id'] = 'did:op:cb36cf78d87f4ce4a784f17c2a4a694f19f3fbf05b814ac6b0b7197163888864'
#     ddo_sample2['service'][2]['metadata']['curation']['rating'] = 0.99
#     mongo.write(ddo_sample2, ddo_sample2['id'])
#     search_model = QueryModel({'price': [0, 12]})
#     assert mongo.query(search_model)[0][0]['id'] == ddo_sample2['id']
#     mongo.delete(ddo_sample['id'])
#     mongo.delete(ddo_sample2['id'])
