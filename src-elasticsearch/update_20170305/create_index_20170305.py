'''
__author__: Jiaming Shen
__description__: Create index with static mapping in ES (a.k.a. define schema). 
'''
import time
import re
import sys
import os
from collections import defaultdict
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

if __name__ == '__main__':
    INDEX_NAME = "pubmed_0305"
    TYPE_NAME = "pubmed_entity"
    NUMBER_SHARDS = 1 # keep this as one if no cluster
    NUMBER_REPLICAS = 0 

    '''
    following is the defined schema
    totally 19 fields: 
    pmid, date, author list, journal name, ( title, abstract, chemical, disease, gene, mutation, species ) with their length, plus total length
    '''
    request_body = {
            "settings": {
            "number_of_shards": NUMBER_SHARDS,
            "number_of_replicas": NUMBER_REPLICAS
        },
        "mappings": {
            TYPE_NAME: {
                "properties": {
                    "pmid": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "date": {
                        "type": "long"
                    },
                    "author_list": {
                        "type": "string", 
                        "index": "not_analyzed"
                    },
                    "journal_name": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "title": { 
                        "type": "string",
                        "similarity": "BM25"
                    },
                    "abstract": {
                        "type": "string",
                        "similarity": "BM25"
                    },
                    "chemical": {
                        "type": "string",
                        "similarity": "BM25"
                    },
                    "disease": {
                        "type": "string",
                        "similarity": "BM25"
                    },
                    "gene": {
                        "type": "string",
                        "similarity": "BM25"
                    },
                    "mutation": {
                        "type": "string",
                        "similarity": "BM25"
                    },
                    "species": {
                        "type": "string",
                        "similarity": "BM25"
                    },
                    "title_length": {
                        "type": "long"
                    },
                    "abstract_length": {
                        "type": "long"
                    },
                    "chemical_length": {
                        "type": "long"
                    },
                    "disease_length": {
                        "type": "long"
                    },
                    "gene_length": {
                        "type": "long"
                    },
                    "mutation_length": {
                        "type": "long"
                    },
                    "species_length": {
                        "type": "long"
                    },
                    "total_length": {
                        "type": "long"
                    }
                }
            }
        }
    }

    es = Elasticsearch()
    if es.indices.exists(INDEX_NAME):
        res = es.indices.delete(index = INDEX_NAME)
        print "Deleting index %s , Response: %s" % (INDEX_NAME, res)
    res = es.indices.create(index = INDEX_NAME, body = request_body)
    print "Create index %s , Response: %s" % (INDEX_NAME, res)