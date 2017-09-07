'''
__author__: Jiaming Shen
__description__: Construct KB from bioconcepts2pubtator_offsets.txt
'''
import time
import re
import sys 
import os
from collections import defaultdict
from collections import Counter

if __name__ == '__main__':
    inputFilePath = "../data/bioconcepts2pubtator_offsets"
    kbFilePath = "../data/kb.txt"

    with open(inputFilePath, "r") as fin:
        start = time.time()
        cnt = 0 # number of document processed
        bulk_size = 5e5 # 
        
        entities = defaultdict(list) # type name -> list of entity mentions
        kb = defaultdict(Counter) # type name -> counter
        for line in fin:
            line = line.strip()
            if not line: # a document end            
                cnt += 1
                if cnt % bulk_size == 0 and cnt != 0:
                    for entity_type in ["chemical", "disease", "gene", "mutation", "species"]:
                        kb[entity_type] += ( Counter(entities[entity_type]) )
                    tmp = time.time()
                    print("processing documents... %s, escaped time %s (seconds)" % ( cnt, tmp - start ) )
                    ## Re-initialize for next bulk of documents
                    entities = defaultdict(list)
                    
            else: # in the middle of a document
                if re.match(r"^\d+\|t\|", line): # title
                    continue
                elif re.match(r"^\d+\|a\|", line): # abstract
                    continue
                else:
                    tmp = line.split("\t")
                    entity_mention = "_".join(tmp[3].split()) # use "_" to connect multiwords entity
                    entity_type = tmp[4].lower()
                    entities[entity_type].append(entity_mention)

        ## indexing those left papers
        for entity_type in ["chemical", "disease", "gene", "mutation", "species"]:
            kb[entity_type] += ( Counter(entities[entity_type]) )
        tmp = time.time()
        print("processing documents... %s, escaped time %s (seconds)" % ( cnt, tmp - start ) )

        end = time.time()
        print("Finish constructing the KB. Total escaped time %s (seconds)" % (end - start) )

    print("Start saving KB")
    with open(kbFilePath, "w") as fout:
        for key in kb:
            entity_mentions = kb[key]
            print(key+"\t"+str(len(entity_mentions))) # type, number of distinct entity mentions
            fout.write("="*20+key+"\t"+str(len(entity_mentions))+"="*20+"\n") # type, number of distinct entity mentions
            for ele in sorted(entity_mentions.items(), key = lambda x:-x[1]):
                fout.write(ele[0]+"\t"+key.upper()+"\t"+str(ele[1])+"\n")