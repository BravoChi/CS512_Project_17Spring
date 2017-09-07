'''
__author__: Jiaming Shen
__description__: Index data from precomputed JSON, which includes latest 5 years PubMed articles
'''
import time
import re
import sys 
import os
import json
from collections import defaultdict
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

if __name__ == '__main__':
    inputFilePath = "../pmid_latest_5years.json"
    logFilePath = "../log_20170430.txt"
    statFilePath = "../stats_20170430.txt"

    INDEX_NAME = "pubmed_0430"
    TYPE_NAME = "pubmed_entity"

    es = Elasticsearch()

    with open(inputFilePath, "r") as fin, open(logFilePath, "w") as fout:
        start = time.time()
        bulk_size = 500 # number of document processed in each bulk index
        bulk_data = [] # data in bulk index
        
        ## saving the sum of all eight lengths for later model usage
        title_length_sum = 0
        abstract_length_sum = 0
        chemical_length_sum = 0
        disease_length_sum = 0
        gene_length_sum = 0
        mutation_length_sum = 0
        species_length_sum = 0
        total_length_sum = 0
            
        cnt = 0
        for line in fin: ## each line is single document
            cnt += 1
            paperInfo = json.loads(line.strip())
            
            data_dict = {}
            total_length = 0
            
            # update PMID
            data_dict["pmid"] = paperInfo["pmid"]
            
            # update title
            data_dict["title"] = paperInfo["title"]
            data_dict["title_length"] = len(paperInfo["title"].split())
            total_length += data_dict["title_length"]
            
            # update abstract
            data_dict["abstract"] = paperInfo["abstract"]
            data_dict["abstract_length"] = len(paperInfo["abstract"].split())
            total_length += data_dict["abstract_length"]
            
            # update date
            data_dict["date"] = paperInfo["date"]
            
            # update author list
            if paperInfo["author"]:
                data_dict["author_list"] = paperInfo["author"].split(";")
            else:
                data_dict["author_list"] = []
                
            # update journal name
            data_dict["journal_name"] = paperInfo["journal"]
            
            # update entities information
            entities = defaultdict(list)
            for ele in paperInfo["entities"]:
                entity_mention = "_".join(ele["name"].split()) # use "_" to connect multi-tokens entity mention
                entity_type = ele["type"].lower() # lower case the type name
                entities[entity_type].append(entity_mention)
            for entity_type in ["chemical", "disease", "gene", "mutation", "species"]:
                tmp = entities[entity_type]
                entity_field = " ".join(tmp) # construct a text field with all entity mentions joined by space
                entity_field_length = len(tmp) # number of entity mention of that type
                total_length += entity_field_length # accumulate each fields for later use
                data_dict[entity_type] = entity_field
                data_dict[entity_type + "_length"] = entity_field_length
            data_dict["total_length"] = total_length
            
            ## update the length status of each field
            title_length_sum += data_dict["title_length"]
            abstract_length_sum += data_dict["abstract_length"]
            chemical_length_sum += data_dict["chemical_length"]
            disease_length_sum += data_dict["disease_length"]
            gene_length_sum += data_dict["gene_length"]
            mutation_length_sum += data_dict["mutation_length"]
            species_length_sum += data_dict["species_length"]
            total_length_sum += data_dict["total_length"]
            
            ## Put current data into the bulk
            op_dict = {
                "index": {
                    "_index": INDEX_NAME,
                    "_type": TYPE_NAME,
                    "_id": data_dict["pmid"]
                }
            }

            bulk_data.append(op_dict)
            bulk_data.append(data_dict)       
                    
            ## Start Bulk indexing
            if cnt % bulk_size == 0 and cnt != 0:
                tmp = time.time()
                es.bulk(index=INDEX_NAME, body=bulk_data, request_timeout = 180)
                fout.write("bulk indexing... %s, escaped time %s (seconds) \n" % ( cnt, tmp - start ) )
                print("bulk indexing... %s, escaped time %s (seconds) " % ( cnt, tmp - start ) )
                bulk_data = []
        
        ## indexing those left papers
        if bulk_data:
            tmp = time.time()
            es.bulk(index=INDEX_NAME, body=bulk_data, request_timeout = 180)
            fout.write("bulk indexing... %s, escaped time %s (seconds) \n" % ( cnt, tmp - start ) )
            print("bulk indexing... %s, escaped time %s (seconds) " % ( cnt, tmp - start ) )
            bulk_data = []

        end = time.time()
        fout.write("Finish indexing. Total escaped time %s (seconds) \n" % (end - start) )
        print("Finish indexing. Total escaped time %s (seconds) " % (end - start) )
        

    print("Start saving statistics \n ")
    with open(statFilePath, "w") as fout:
        fout.write("NUM_PAPER = %s\n" % cnt)
        fout.write("TITLE_LENGTH_SUM = %s\n" % title_length_sum)
        fout.write("ABSTRACT_LENGTH_SUM = %s\n" % abstract_length_sum)
        fout.write("CHEMICAL_LENGTH_SUM = %s\n" % chemical_length_sum)
        fout.write("DISEASE_LENGTH_SUM = %s\n" % disease_length_sum)
        fout.write("GENE_LENGTH_SUM = %s\n" % gene_length_sum)
        fout.write("MUTATION_LENGTH_SUM = %s\n" % mutation_length_sum)
        fout.write("SPECIES_LENGTH_SUM = %s\n" % species_length_sum)
        fout.write("TOTAL_LENGTH_SUM = %s\n" % total_length_sum)

