import sys
import time
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from collections import Counter
from collections import defaultdict

class ES():
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

        ## Model configuration parameters
        # EPS = 1e-100 # prevent log underflow
        # TYPE_IMPORTANT_FLAG = 1  # determine whether term is weighted using inverse type frequency
        # TYPE_INTERACTION_FLAG = 1 # determine whether term/type interaction is employeed
        # TIME_BOOSTING_FLAG = 1 # determine whether we use time boosting 
        # TYPE_DIST_SCORE_FLAG = 1 # determine whether we calcuate the type distribution score
        # DEBUG_CHECK_MATCHED_TERMS = 0 # DEBUG_FLAG

        # CUR_YEAR = 2016 # time boosting parameters
        # WINDOW_YEAR = 7  # time boostring parameters
        # MU_ALPHA = 2000.0 # smoothing parameter for type distribution
        # MU_THETA = 2000.0 # smoothing parameter for token distribution  
        # INTERACTION_STRENGTH = 10
        # TITLE_WIGHTS = 16
        # ABSTRACT_WIGHTS = 3
        # TYPE_WIGHTS = 16 
        
        self.es = Elasticsearch()

    def search(self, query):
        res = self.es.search(
            index = self.INDEX_NAME,
            request_timeout = self.RQUEST_TIMEOUT,
            body = {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "match": {
                                    "title": query
                                }
                            },
                            {
                                "match": {
                                    "abstract": query
                                }
                            }
                        ]
                    }
                }
            }
        )
        return res
        # # print res['took']
        # print res['hits']['total']
        # print res['hits']['hits']
        # for hit in res['hits']['hits']:
        #     print hit["score"]

# print "Finish elasticsearch retrieval, start analyzing in details"
# print "Search uses time = %s (millisecond)" % res['took']
# print "Number of hits = %s" % res['hits']['total']
# rank = 1
# for hit in res['hits']['hits'][:topK]:
#     print "Rank =", rank, "PMID =", hit["_source"]["pmid"], "Score =", hit["_score"], "Date =", hit["_source"]["date"]
#     print "Title:", hit["_source"]["title"]
# #     print "Abstract:", hit["_source"]["abstract"]
#     match_keywords_title = match_keywords(hit["_source"]["title"], QUERY_TOKENS, multi_term_tokens)
#     print "Number of matched terms in title: ", len(match_keywords_title), "|", match_keywords_title
#     match_keywords_abstract = match_keywords(hit["_source"]["abstract"], QUERY_TOKENS, multi_term_tokens)
#     print "Number of matched terms in abstract: ", len(match_keywords_abstract), "|", match_keywords_abstract
#     print "="*20
#     rank += 1



