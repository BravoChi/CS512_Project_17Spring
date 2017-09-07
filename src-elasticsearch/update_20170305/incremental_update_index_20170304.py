'''
__author__: Jiaming Shen
__description__: Update index of "pubmed_1211", add in author list and journal name information
'''
import time
import re
import sys 
import os
from collections import defaultdict
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

if __name__ == '__main__':
    # inputFilePath = "./indexer2/bioconcepts2pubtator_offsets.sample"
    # logFilePath = "./log.txt"
    # statFilePath = "./stats.txt"
    # dateFilePath = "./indexer2/pmid2date.txt"

    inputFilePath = "../data/pmid2authorAndJounralName.txt"
    logFilePath = "../data/log_update_20170304.txt"
    # statFilePath = "../data/stats.txt"
    # dateFilePath = "../data/pmid2date.txt"
    
    INDEX_NAME = "pubmed_1211"
    TYPE_NAME = "pubmed_entity"

    es = Elasticsearch()

    with open(inputFilePath, "r") as fin, open(logFilePath,"w") as fout:
        start = time.time()
        bulk_cnt = 0 # number of document processed
        bulk_size = 1000 # number of document processed in each bulk index
        bulk_data = [] # data in bulk index

        cnt = 0
        for line in fin:
            line = line.strip()
            if cnt % 4 == 0:
                pmid = line
            elif cnt % 4 == 1:
                cnt += 1
                continue
            elif cnt % 4 == 2:
                author_list = line.split(";")
            elif cnt % 4 == 3: # a full document is seen
                journal_name = line

                # print(pmid)
                # print(author_list)
                # print(journal_name)
                # print("="*40)

                op_dict = {
                    "update": { # not index!!! Extremelly Important!!!
                        "_index": INDEX_NAME,
                        "_type": TYPE_NAME,
                        "_id": pmid
                    }
                }

                ## Put current data into the bulk
                bulk_data.append(op_dict)

                data_dict = {
                    "script": {
                        "inline": """
                            ctx._source.author_list = authorList;
                            ctx._source.journal_name = journalName;
                        """,
                        "params": {
                            "authorList": author_list,
                            "journalName": journal_name
                        }
                    },
                    "upsert": {}
                }

                bulk_data.append(data_dict)
                bulk_cnt += 1

                ## Start Bulk indexing
                if bulk_cnt % bulk_size == 0 and bulk_cnt != 0:
                    tmp = time.time()
                    es.bulk(index=INDEX_NAME, body=bulk_data, request_timeout = 180)
                    fout.write("bulk updating... %s, escaped time %s (seconds) \n" % ( bulk_cnt, tmp - start ) )
                    print("bulk updating... %s, escaped time %s (seconds) " % ( bulk_cnt, tmp - start ) )
                    bulk_data = [] 

            cnt += 1


        # indexing those left papers
        tmp = time.time()
        es.bulk(index=INDEX_NAME, body=bulk_data, request_timeout = 180)
        fout.write("bulk updating... %s, escaped time %s (seconds) \n" % ( bulk_cnt, tmp - start ) )
        print("bulk updating... %s, escaped time %s (seconds) " % ( bulk_cnt, tmp - start ) )
        bulk_data = []

        end = time.time()
        fout.write("Finish updating. Total escaped time %s (seconds) \n" % (end - start) )
        print("Finish updating. Total escaped time %s (seconds) " % (end - start) )


