import sys
import time
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from collections import Counter
from collections import defaultdict

class ES2():
    def __init__(self,index_name,topK=20, rescore_window_size=1000,request_timeout=180):
        '''
        All Parameter settings 
        '''
        ## Elasticsearch configuration parameters
        self.topK = topK
        self.rescore_window_size = rescore_window_size # rescoreing window size
        self.RQUEST_TIMEOUT = request_timeout # timeout limit in second
        self.QUERY_WEIGHT = 0 # set 0 if you want to use our own model
        self.RESCORE_WEIGHT = 1 # set 1 if you want to use our own model

        ## Corpus/Index Information/Statistics (keep fixed, unless corpus indexes are changed)
        self.INDEX_NAME = index_name
        self.TYPE_POP = [306534793.0, 3072116820.0, 67678792.0, 79961123.0, 30860984.0, 1.0, 51730932.0, 3608883444]
        self.TYPE2INDEX = ["title", "abstract", "chemical", "disease", "gene", "mutation", "species", "total"]

        ## Model parameter
        self.TITLE_WIGHTS = 16
        self.ABSTRACT_WIGHTS = 3

        self.es = Elasticsearch()

    def entity_detection(self, query):
        '''
        query: string
        '''
        # highlight_term_list = []
        highlight_term_list = [ele.lower() for ele in query.split(", ")]
        return highlight_term_list

    def entity_typing(self, entity_list):
        '''
        entity_list: list of string
        '''
        highlight_term_list_w_color = []
        for entity in entity_list:
            # term_type = getType(term) # get the entity type
            # color = type2color[term_type] # different entity type to different color
            if entity == "prostate cancer" or entity == "cancer":
                color = "r"
                highlight_term_list_w_color.append([entity, color])
            else:
                color = "b"
                highlight_term_list_w_color.append([entity, color])
        return highlight_term_list_w_color

    def generate_search_body(self, query_term_list):
        '''
        query_term_list: a list of string
        '''
        single_term_token = []
        multiple_term_token = []
        for query_term in query_term_list:
            if len(query_term.split()) > 1:
                multiple_term_token.append(query_term)
            else:
                single_term_token.append(query_term)

        FISRT_ROUND_SINGLE_TOEKN = " ".join(single_term_token)
        should_list = []
        field2weights = {"title": self.TITLE_WIGHTS, "abstract": self.ABSTRACT_WIGHTS}
        for ele in multiple_term_token:
            for field in ["title", "abstract"]:
                tmp = {"match_phrase":{field:{"query":ele,"boost":field2weights[field]}}}
                should_list.append(tmp)

        print should_list


        search_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": FISRT_ROUND_SINGLE_TOEKN,
                                "type": "most_fields",
                                "fields": ["title^16","abstract^3"]
                            }
                        },
                        {
                            "bool": {
                                "should": should_list
                            }
                        }
                    ]
                }                    
            }
        }

        return search_body


    def search(self, search_body):
        res = self.es.search(
            index = self.INDEX_NAME,
            request_timeout = self.RQUEST_TIMEOUT,
            body = search_body
        )
        return res
