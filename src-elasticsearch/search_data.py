'''
__author__: Jiaming Shen
__description__: Implement query processing and expansion
'''
import sys
import time
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from collections import Counter
from collections import defaultdict
from textblob import TextBlob
import math

'''
Expand raw query into real searched query (with type and fields information)
'''
def query_expansion_with_type(raw_query_list, raw_type_list = None):
    '''
    raw_query_list: a list of query terms(single/multi words)
    raw_type_list: a list of types corresponding to each query term (if None, we need to type it ourselves)
    '''
    L_q = len(raw_query_list)
    raw_query_list = [ele.lower() for ele in raw_query_list] #lower case transformation
    if not raw_type_list:
        raw_type_list = []
        for ele in raw_query_list:
            ele_type = "NOI" # later we need to map the type it ourselves
            raw_type_list.append(ele_type.lower())
    else:
        raw_type_list = [ele.lower() for ele in raw_type_list]
        
    if len(raw_query_list) != len(raw_type_list):
        print "Number of query tokens and their types are unmatched"
        return 0
    
    single_term_tokens = []
    single_term_tokens_type = []
    single_term_tokens_weight = [] 

    multi_term_tokens = []
    
    multi_term_tokens_with_sep = [] 
    multi_term_tokens_with_sep_type = []
    multi_term_tokens_with_sep_weight = []

    type2freq = Counter(raw_type_list)
    for i, token in enumerate(raw_query_list):
        if len(token.split()) > 1: # multi-token query
            multi_term_tokens.append(token)
            
            multi_term_tokens_with_sep.append("_".join(token.split()))
            multi_term_tokens_with_sep_type.append(raw_type_list[i])
            weight = math.log(1 + 1.0*L_q/type2freq[raw_type_list[i]])
            multi_term_tokens_with_sep_weight.append(weight)
        else:
            single_term_tokens.append(token)
            single_term_tokens_type.append(raw_type_list[i])
            weight = math.log(1 + 1.0*L_q/type2freq[raw_type_list[i]])
            single_term_tokens_weight.append(weight)
    
    L_st = len(single_term_tokens)
    L_mt = len(multi_term_tokens_with_sep)
    QUERY_TOKENS = single_term_tokens * 3 + multi_term_tokens_with_sep * 3
    TOKEN_TYPES = ["title"]*L_st + ["abstract"]*L_st + single_term_tokens_type + \
                  ["title"]*L_mt + ["abstract"]*L_mt + multi_term_tokens_with_sep_type
        
    TOKEN_IMPORTANTCE = [TITLE_WIGHTS*weight for weight in single_term_tokens_weight] + \
                        [ABSTRACT_WIGHTS*weight for weight in single_term_tokens_weight] + \
                        [TYPE_WIGHTS*weight for weight in single_term_tokens_weight] + \
                        [TITLE_WIGHTS*weight for weight in multi_term_tokens_with_sep_weight] + \
                        [ABSTRACT_WIGHTS*weight for weight in multi_term_tokens_with_sep_weight] + \
                        [TYPE_WIGHTS*weight for weight in multi_term_tokens_with_sep_weight] 
    
    FISRT_ROUND_SINGLE_TOEKN = " ".join(single_term_tokens)
           
    return FISRT_ROUND_SINGLE_TOEKN, multi_term_tokens, QUERY_TOKENS, TOKEN_TYPES, TOKEN_IMPORTANTCE

'''
Calculate matched keywords in postprecosing
'''
def match_keywords(text, query_single_word_list, query_multi_word_w_sep_list = None, type_field = 0):
    '''
    text: a string represents a piece of text
    query_single_word_list: a list of query single-token terms
    query_multi_word_w_sep_list: a list of query multi-token terms *with* seperator
    type_field: whether text is title/abstract (0) or a type field (1)
    return a counter with matched terms as key and matched frequency as value
    
    '''
    if not type_field: # in abstract/title 
        text = text.lower()
        blob = TextBlob(text)
        matched = []
        for word in blob.words:
            if word in query_single_word_list:
                matched.append(word)
    
        if query_multi_word_w_sep_list: 
            for ele in query_multi_word_w_sep_list:
                if " ".join(ele.split("_")) in text:
                    matched.append(ele)
    
    else: # in type_field
        text = text.lower()
        for word in text.split():
            if word in query_single_word_list:
                matched.append(word)
            if word in query_multi_word_w_sep_list:
                matched.append(word)
                
    c = Counter(matched)         
    return c

if __name__ == '__main__':
    '''
    All Parameter settings 
    '''
    ## Elasticsearch configuration parameters
    topK = 20
    rescore_window_size = 10000 # rescoreing window size
    RQUEST_TIMEOUT = 180 # timeout limit in second
    QUERY_WEIGHT = 0 # set 0 if you want to use our own model
    RESCORE_WEIGHT = 1 # set 1 if you want to use our own model

    ## Corpus/Index Information/Statistics (keep fixed, unless corpus indexes are changed)
    INDEX_NAME = "pubmed_1211" 
    TYPE_POP = [306534793.0, 3072116820.0, 67678792.0, 79961123.0, 30860984.0, 1.0, 51730932.0, 3608883444]
    TYPE2INDEX = ["title", "abstract", "chemical", "disease", "gene", "mutation", "species", "total"]

    ## Model configuration parameters
    EPS = 1e-100 # prevent log underflow
    TYPE_IMPORTANT_FLAG = 1  # determine whether term is weighted using inverse type frequency
    TYPE_INTERACTION_FLAG = 1 # determine whether term/type interaction is employeed
    TIME_BOOSTING_FLAG = 1 # determine whether we use time boosting 
    TYPE_DIST_SCORE_FLAG = 1 # determine whether we calcuate the type distribution score
    DEBUG_CHECK_MATCHED_TERMS = 0 # DEBUG_FLAG

    CUR_YEAR = 2016 # time boosting parameters
    WINDOW_YEAR = 7  # time boostring parameters
    MU_ALPHA = 2000.0 # smoothing parameter for type distribution
    MU_THETA = 2000.0 # smoothing parameter for token distribution  
    INTERACTION_STRENGTH = 10
    TITLE_WIGHTS = 16
    ABSTRACT_WIGHTS = 3
    TYPE_WIGHTS = 16 

    '''
    Expand query 
    '''
    ## Raw query is the expected user input query
    raw_query_string = "gabp, tert, cd11b, foxp2, cancer" 
    # raw_query_string = "AR, BRCA1, BRCA2, CD82, CDH1, CHEK2, EHBP1, ELAC2, EP300, EPHB2, EZH2, FGFR2, FGFR4, GNMT, HNF1B, HOXB13, HPCX, IGF2, ITGA6, KLF6, LRP2, MAD1L1, MED12, MSMB, MSR1, MXI1, NBN, PCAP, PCNT, PLXNB1, PTEN, RNASEL, SRD5A2, STAT3, TGFBR1, WRN, WT1, ZFHX3, prostate cancer"
    # raw_query_string = "C9orf72, SOD1, TARDBP, FUS, ALS2, ANG, ATXN2, CHCHD10, CHMP2B, DCTN1, ERBB4, FIG4, HNRNPA1, MATR3, NEFH, OPTN, PFN1, PRPH, SETX, SIGMAR1, SMN1, SPG11, SQSTM1, TBK1, TRPM7, TUBA4A, UBQLN2, VAPB, VCP, amyotrophic lateral sclerosis"
    raw_query_list = raw_query_string.split(", ")
    raw_types_list = ["gene"]*len(raw_query_list)
    raw_types_list[-1] = "disease"

    FISRT_ROUND_SINGLE_TOEKN, multi_term_tokens, QUERY_TOKENS, TOKEN_TYPES, TOKEN_IMPORTANTCE = query_expansion_with_type(raw_query_list, raw_types_list)
    should_list = []
    field2weights = {"title": TITLE_WIGHTS, "abstract": ABSTRACT_WIGHTS}
    for ele in multi_term_tokens:
        for field in ["title", "abstract"]:
            tmp = {"match_phrase":{field:{"query":ele,"boost":field2weights[field]}}}
            should_list.append(tmp)
    print should_list

    # print "=== FISRT_ROUND_SINGLE_TOEKN = ", FISRT_ROUND_SINGLE_TOEKN
    # print "=== multi_term_tokens = ", multi_term_tokens
    # print "=== QUERY_TOKENS = ", QUERY_TOKENS
    # print "=== TOKEN_TYPES = ", TOKEN_TYPES
    # print "=== TOKEN_IMPORTANTCE =" , TOKEN_IMPORTANTCE

    '''
    Start ElasticSearch
    '''
    es = Elasticsearch()

    ## GC-ELM in rescoring 
    res = es.search(
        index = INDEX_NAME,
        request_timeout = RQUEST_TIMEOUT,
        body = {
            "size": topK,
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
            ,"rescore": {
                "window_size": rescore_window_size,
                "query": {
                    "rescore_query": {
                        "function_score": {
                            "functions": [
                                {
                                    "script_score": {
                                        "params": {
                                            "eps": EPS, # add for log 
                                            "mu_alpha": MU_ALPHA,
                                            "mu_theta": MU_THETA,
                                            "interaction_strength": INTERACTION_STRENGTH, 
                                            "type2index" : TYPE2INDEX,
                                            "type_pop": TYPE_POP, 
                                            "cur_year": CUR_YEAR,
                                            "window_year": WINDOW_YEAR,
                                            "type_importance_flag": TYPE_IMPORTANT_FLAG,
                                            "type_interaction_flag": TYPE_INTERACTION_FLAG,
                                            "time_boosting_flag": TIME_BOOSTING_FLAG,
                                            "type_dist_score_flag": TYPE_DIST_SCORE_FLAG,
                                            "tokens" : QUERY_TOKENS,
                                            "types" : TOKEN_TYPES,
                                            "token_importance": TOKEN_IMPORTANTCE,
                                            "DEBUG_CHECK_MATCHED_TERMS": DEBUG_CHECK_MATCHED_TERMS
                                        },
                                        "script": """
                                            total_score = 0.0;
                                            // boost based on token type interaction; 
                                            number_matched_terms = 0;
                                            if (type_interaction_flag > 0) {;
                                                for (int i = 0; i < tokens.size(); ++i) {;
                                                    token = tokens[i];
                                                    token_type = types[i];
                                                    if (_index[token_type][token].tf() > 0 ) {;
                                                        number_matched_terms += 1;
                                                    };
                                                };
                                            };

                                            if (DEBUG_CHECK_MATCHED_TERMS > 0) {;
                                                total_score = number_matched_terms;
                                                return total_score;
                                            };

                                            for (int i = 0; i < tokens.size(); ++i) {;
                                                cur_score = 0.0;
                                                token = tokens[i];
                                                token_type = types[i];
                                                token_type_length = token_type + "_length";
                                                token_type_index = type2index.indexOf(token_type);

                                                // score for token under that type;
                                                tf_d = _index[token_type][token].tf();
                                                tf_D = _index[token_type][token].ttf();
                                                L_d = doc[token_type_length].value;
                                                L_D = type_pop[token_type_index];
                                                cur_score = cur_score + log(eps + (tf_d + mu_theta*(tf_D/L_D) )/(L_d + mu_theta));

                                                // score for that token's type;
                                                if (type_dist_score_flag > 0) {;
                                                    tf_d = doc[token_type_length].value;
                                                    tf_D = type_pop[token_type_index];
                                                    L_d = doc["total_length"].value;
                                                    L_D = type_pop[-1]; 
                                                    cur_score = cur_score + log(eps + (tf_d + mu_alpha*(tf_D/L_D) )/(L_d + mu_alpha));
                                                };
                                                
                                                token_weight = 0;

                                                // boost based on that token type's importance;
                                                if (type_importance_flag > 0) {;
                                                    token_weight = token_importance[i];
                                                };

                                                // boost based on token type interaction; 
                                                if ( type_interaction_flag > 0) {;
                                                    token_weight += (number_matched_terms * interaction_strength);                                 
                                                };

                                                if ( type_importance_flag > 0 || type_interaction_flag > 0) {;
                                                    cur_score = (1.0 / token_weight) * cur_score;
                                                };

                                                total_score = total_score + cur_score;
                                            };

                                            // add in time boosting factor;
                                            if (time_boosting_flag > 0) {;
                                                p_year = doc["date"].value;
                                                if (cur_year - p_year > window_year) {;
                                                   factor = 1.0; 
                                                } else{ // boost recently published paper; 
                                                   factor = (1 + (p_year - cur_year + window_year)/10.0);
                                                };
                                                total_score = total_score / factor;
                                            };
                                            return total_score;
                                        """
                                    }
                                }
                            ],
                            "score_mode": "sum",
                            "boost_mode": "replace"
                        }
                    },
                    "query_weight": QUERY_WEIGHT,
                    "rescore_query_weight": RESCORE_WEIGHT
                }
            }
        }
    )

    print "Finish elasticsearch retrieval, start analyzing in details"
    print "Search uses time = %s (millisecond)" % res['took']
    print "Number of hits = %s" % res['hits']['total']
    rank = 1
    for hit in res['hits']['hits'][:topK]:
        print "Rank =", rank, "PMID =", hit["_source"]["pmid"], "Score =", hit["_score"], "Date =", hit["_source"]["date"]
        print "Title:", hit["_source"]["title"]
        match_keywords_title = match_keywords(hit["_source"]["title"], QUERY_TOKENS, multi_term_tokens)
        print "Number of matched terms in title: ", len(match_keywords_title), "|", match_keywords_title
        match_keywords_abstract = match_keywords(hit["_source"]["abstract"], QUERY_TOKENS, multi_term_tokens)
        print "Number of matched terms in abstract: ", len(match_keywords_abstract), "|", match_keywords_abstract
        print "="*20
        rank += 1

    '''
    Save results to files
    '''
    fileDirPath = "../exp-result/"
    model = "GC-ELM-query1"
    topK = 20
    with open(fileDirPath+model+".txt", "w") as fout:
        fout.write("Search uses time = %s (millisecond)\n" % res['took'])
        fout.write("Number of hits = %s\n" % res['hits']['total'])
        for hit in res['hits']['hits'][:topK]:
            fout.write("PMID= %s, Score= %s, Date= %s\n" % (hit["_source"]["pmid"], hit["_score"], hit["_source"]["date"]))
            fout.write("Title: %s\n" % hit["_source"]["title"])
            
            match_keywords_title = match_keywords(hit["_source"]["title"], QUERY_TOKENS, multi_term_tokens)
            fout.write("Number of matched terms in title: %s | %s \n" % (len(match_keywords_title), str(match_keywords_title)))
            match_keywords_abstract = match_keywords(hit["_source"]["abstract"], QUERY_TOKENS, multi_term_tokens)
            fout.write("Number of matched terms in abstract: %s | %s \n" % (len(match_keywords_abstract), str(match_keywords_abstract)))
            fout.write("="*20+"\n")
