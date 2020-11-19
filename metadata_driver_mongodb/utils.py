import logging
from datetime import datetime, timedelta

import metadata_driver_mongodb.indexes as index

logger = logging.getLogger(__name__)

AND = "$and"
OR = "$or"
GT = "$gte"
LT = "$lte"


def query_parser(query):
    query_result = {}
    for key in query.items():
        if 'price' in key:
            create_price_query(query, query_result)
        elif 'license' in key:
            create_query(query['license'], index.license, query_result, OR)
        elif 'categories' in key:
            create_query(query['categories'], index.categories, query_result, OR)
        elif 'tags' in key:
            create_query(query['tags'], index.tags, query_result, OR)
        elif 'type' in key:
            create_query(query['type'], index.service_type, query_result, AND)
        elif 'updateFrequency' in key:
            create_query(query['updateFrequency'], index.updated_frequency, query_result, OR)
        elif 'created' in key:
            create_created_query(query, query_result)
        elif 'sample' in key:
            query_result[index.sample] = 'sample'
        elif 'text' in key:
            create_text_query(query['text'], query_result)
        else:
            logger.error('The key %s is not supported by MetadataDB.' % key[0])
            raise Exception('The key %s is not supported by MetadataDB.' % key[0])
    return query_result


def create_query(value, index, query, operator):
    for i, _ in enumerate(value):
        if i == 0:
            if operator in query:
                query[operator] += [{index: value[i]}]
            else:
                query[operator] = [{index: value[i]}]
        else:
            query[operator] += [{index: value[i]}]
    return query


def create_price_query(query, query_result):
    if len(query['price']) > 2:
        logger.info('You are sending more values than needed.')
    elif len(query['price']) == 0:
        logger.info('You are not sending any value.')
    elif len(query['price']) == 1:
        query_result[index.price] = {GT: 0, LT: query['price'][0]}
    else:
        query_result[index.price] = {GT: query['price'][0], LT: query['price'][1]}
    return query_result


def create_created_query(query, query_result):
    now = datetime.now() - timedelta(weeks=1000)
    for values in query['created']:
        if values == 'today':
            now = datetime.now() - timedelta(days=1)
        elif values == 'lastWeek':
            now = datetime.now() - timedelta(days=7)
        elif values == 'lastMonth':
            now = datetime.now() - timedelta(days=30)
        elif values == 'lastYear':
            now = datetime.now() - timedelta(days=365)
        else:
            logger.info('The key %s is not supported in the created query' % values)
    query_result['created'] = {GT: now}
    return query_result


def create_text_query(query, query_result):
    query_result['$text'] = {"$search": query[0]}
    return query_result
