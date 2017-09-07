'''
__author__: Jiaming Shen
__description__: Update the mapping (introduce two fields) in existing index in ES (a.k.a. update schema). 
'''
import time
import re
import sys
import os
from collections import defaultdict
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


if __name__ == '__main__':
    INDEX_NAME = "pubmed_1211" # existing index name
    TYPE_NAME = "pubmed_entity" # existing type name

    es = Elasticsearch()

    if es.indices.exists(INDEX_NAME):
        request_body = {
            "properties": {
                "author_list": {
                    "type": "string", 
                    "index": "not_analyzed"
                },
                "journal_name": {
                    "type": "string",
                    "index": "not_analyzed"
                }
            }
        }
        res = es.indices.put_mapping(index = INDEX_NAME, doc_type = TYPE_NAME, body = request_body)
        print res
    
