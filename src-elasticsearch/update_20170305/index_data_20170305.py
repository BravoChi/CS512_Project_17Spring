'''
__author__: Jiaming Shen
__description__: Parse and index bioconcepts2pubtator_offsets.txt
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

    inputFilePath = "../../data/bioconcepts2pubtator_offsets"
    logFilePath = "../../data/log_20170305.txt"
    statFilePath = "../../data/stats_20170305.txt"
    dateFilePath = "../../data/pmid2date.txt"
    ajFilePath = "../../data/pmid2authorAndJounralName.txt"
    
    INDEX_NAME = "pubmed_0305"
    TYPE_NAME = "pubmed_entity"

    pmid2date = defaultdict(int)
    start = time.time()
    with open(dateFilePath, "r") as fin:
        for line in fin:
            line = line.strip()
            if line:
                tmp = line.split("\t")
                if len(tmp) == 2:
                    pmid = tmp[0]
                    try:
                        date = int(tmp[1])
                    except:
                        date = 0
                pmid2date[pmid] = date
    end = time.time()
    print("Finish loading pmid2date file, using time %s (secondes)" % (end-start))   

    pmid2authorList = defaultdict(list)
    pmid2journalName = defaultdict()
    
    start = time.time()
    cnt = 0
    with open(ajFilePath, "r") as fin:
        for line in fin:
            line = line.strip()
            if line:
                if cnt % 4 == 0:
                    pmid = line
                elif cnt % 4 == 1:
                    cnt += 1
                    continue
                elif cnt % 4 == 2:
                    author_list = line.split(";")
                elif cnt % 4 == 3: # a full document is seen
                    journal_name = line

                    pmid2authorList[pmid] = author_list
                    pmid2journalName[pmid] = journal_name

                cnt += 1
                
    end = time.time()
    print("Finish loading pmid2authorAndJounralName file, using time %s (secondes)" % (end-start))   

    es = Elasticsearch()

    with open(inputFilePath, "r") as fin, open(logFilePath, "w") as fout:
        start = time.time()
        cnt = 0 # number of document processed
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
        
        title = ""
        abstract = ""
        pmid = ""
        date = 0
        entities = defaultdict(list) # In the order of CDGMS == Chemical, Disease, Gene, Mutation, Species
        for line in fin:
            line = line.strip()
            if not line: # a document end
                ## Construct a data_dict for later indexing
                data_dict = {}
                total_length = 0
                data_dict["pmid"] = pmid

                if pmid in pmid2date:
                    data_dict["date"] = pmid2date[pmid]
                else:
                    data_dict["date"] = 0

                if pmid in pmid2authorList:
                    data_dict["author_list"] = pmid2authorList[pmid]
                else:
                    data_dict["author_list"] = []

                if pmid in pmid2journalName:
                    data_dict["journal_name"] = pmid2journalName[pmid]
                else:
                    data_dict["journal_name"] = ""

                data_dict["title"] = title
                data_dict["title_length"] = len(title.split())
                total_length += data_dict["title_length"]
                data_dict["abstract"] = abstract
                data_dict["abstract_length"] = len(abstract.split())
                total_length += data_dict["abstract_length"]

                for entity_type in ["chemical", "disease", "gene", "mutation", "species"]:
                    tmp = entities[entity_type]
                    entity_field = " ".join(tmp) # construct a text field with all entity mentions joined by space
                    entity_field_length = len(tmp)
                    total_length += entity_field_length # accumulate each fields for later use
                    data_dict[entity_type] = entity_field
                    data_dict[entity_type + "_length"] = entity_field_length
                data_dict["total_length"] = total_length
                
                ## Update the length stats of each field
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
                            
                ## Re-initialize for next document
                title = ""
                abstract = ""
                pmid = ""
                entities = defaultdict(list)
                cnt += 1
                
                ## Start Bulk indexing
                if cnt % bulk_size == 0 and cnt != 0:
                    tmp = time.time()
                    es.bulk(index=INDEX_NAME, body=bulk_data, request_timeout = 180)
                    fout.write("bulk indexing... %s, escaped time %s (seconds) \n" % ( cnt, tmp - start ) )
                    print("bulk indexing... %s, escaped time %s (seconds) " % ( cnt, tmp - start ) )
                    bulk_data = []
                    
            else: # in the middle of a document
                if re.match(r"^\d+\|t\|", line): # title
                    pmid = line.split("|t|")[0]
                    title = line.split("|t|")[1]
                elif re.match(r"^\d+\|a\|", line): # abstract
                    abstract = line.split("|a|")[1]
                else:
                    tmp = line.split("\t")
                    entity_mention = "_".join(tmp[3].split()) # use "_" to connect multiwords entity
                    entity_type = tmp[4].lower()
                    entities[entity_type].append(entity_mention)

        ## indexing those left papers
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


