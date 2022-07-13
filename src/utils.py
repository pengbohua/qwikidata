from elasticsearch import Elasticsearch
import json
from pprint import pprint
import time

def get_parsed_main_result(es_body, query_body, index="property"):
    res = es_body.search(index=index,
                body=query_body,
                request_timeout=20,
                size=1000
                )

    # search property first
    PIDs = []
    labels = []
    descriptions = []
    full_messages = []
    highlight_labels = []
    highlight_descriptions = []
    for i, search_it in enumerate(res['hits']['hits']):
        PIDs.append(search_it["_source"]['id'])
        # for debugging
        descriptions.append(search_it["_source"]['description'])
        full_messages.append(search_it["_source"]['message'])
        labels.append(search_it["_source"]["label"])
        # highlights exist only if query keyword exists
        try:
            highlight_labels.append(search_it["highlight"]['label'])
        except KeyError:
            highlight_labels.append(search_it["_source"]["label"])
        try:
            highlight_descriptions.append(search_it["highlight"]['description'])
        except:
            highlight_descriptions.append(search_it["_source"]['description'])
    return {"id_set":PIDs, 'label':labels, 'description': descriptions, "full_message":full_messages,
            'hl_label':highlight_labels, 'hl_desc':highlight_descriptions}


def get_parsed_alias(es_body, query_aliases, index="propertyalias", original_index="property", **kwargs):
    id_results = set(kwargs['id_set'])
    # search within aliases
    res = es_body.search(index=index,
                body=query_aliases,
                request_timeout=20,
                size=1000
                )

    def id_query(ori_id):
        return {"query":{
                "term": {
                "id": ori_id
                }}}

    PIDs = kwargs['id_set']
    labels = kwargs['label']
    descriptions = kwargs['description']
    full_messages = kwargs['full_message']
    highlight_labels = kwargs['hl_label']
    highlight_descriptions = kwargs['hl_desc']
    for i, search_it in enumerate(res['hits']['hits']):
        id = search_it["_source"]['id']
        if id in id_results:
            continue
        else:
            # find original document of this alias
            id_search = es_body.search(index=original_index,
                                 body=id_query(id),)
            try:
                id_res = id_search["hits"]['hits'][0]
            except KeyError:
                continue
            PIDs.append(id)
            id_results.add(id)
            # add original info of the alias
            labels.append(id_res["_source"]['label'])
            descriptions.append(id_res["_source"]['description'])
            full_messages.append(id_res["_source"]['message'])

            # highlights share the same info with labels and descs in this case
            highlight_labels.append(id_res["_source"]['label'])
            highlight_descriptions.append(id_res["_source"]['description'])

    return {"id_set":PIDs, 'label':labels, 'description': descriptions, "full_message":full_messages,
            'hl_label':highlight_labels, 'hl_desc':highlight_descriptions}



