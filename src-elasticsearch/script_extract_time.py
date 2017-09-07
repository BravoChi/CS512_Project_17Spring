'''
__author__: Jiaming Shen
__description__: Extract the date information of each paper from Yu's 30G PubMed files
'''
import time

if __name__ == "__main__":
    inputFilePath = "/data/yushi2/full_pubmed/data_parsed/pmid2meta.txt"
    
    inputFilePath = "./sample_PMC_new.txt"
    outputFilePath = "../data/pmid2date.txt"
    
    start = time.time()
    CHUNK_SIZE = 1e5
    with open(inputFilePath,"r") as fin, open(outputFilePath, "w") as fout:
        document = []
        cnt = 0 
        for line in fin:
            line = line.strip()
            if cnt % 4 == 0:
                pmid = line
                # print pmid
            elif cnt % 4 == 1:
                date = line
                # print date
            elif cnt % 4 == 2:
                cnt += 1
                continue
            elif cnt % 4 == 3: ## a full document is seen
                fout.write(pmid + "\t" + date + "\n")

            cnt += 1

            if cnt % CHUNK_SIZE == 0 and cnt != 0:
                print cnt


        end = time.time()
        print("Finish parsing pmid2date, using time %s (seconds) \n" % (end - start))

