import sys 
sys.path.append("..") 
import numpy as np
from copy import copy

from Triplet import Triplet, MTriplet, TSchema, Query
try:
    from trans_utils import us_en_synonym, _random_choice
except:
    from transformations.trans_utils import us_en_synonym, _random_choice

def sup_substitute(triplet):
    
    superlative_adjective_synonym = {
        "max": ["highest", "largest", "biggest", "max", "maximal"],
        "min": ["lowest", "least", "smallest", "min", "minimal"]
    }


    candidate = []
    for key in superlative_adjective_synonym.keys():
        for i, synonym in enumerate(superlative_adjective_synonym[key]):
            if synonym in triplet.utterance:
                start_idx = triplet.utterance.index(synonym)
                end_idx = start_idx + len(synonym)
                for subs_syn in superlative_adjective_synonym[key]:
                    if subs_syn == synonym:continue
                    candidate.append(triplet.utterance[:start_idx]+subs_syn+triplet.utterance[end_idx:])
    
    mutations = []
    for c in candidate:  
        mutations.append(MTriplet(triplet, utterance=c))
    
    return mutations

# def num_substitute(triplet):
    
#     numeric_synonym = {
#         "0": ["0", "zero"],
#         "1": ["1", "one"],
#         "2": ["2", "two"],
#         "3": ["3", "three"],
#         "4": ["4", "four"],
#         "5": ["5", "five"],
#         "6": ["6", "six"],
#         "7": ["7", "seven"],
#         "8": ["8", "eight"],
#         "9": ["9", "nine"],
#     }

#     candidate = []
#     for key in numeric_synonym:
#         for i, synonym in enumerate(numeric_synonym[key]):
#             if synonym in triplet.utt_tok:
#                 word_idx = triplet.utt_tok.index(synonym)
#                 syn_idx = 1 if i == 0 else 0
#                 candidate.append((word_idx, numeric_synonym[key][syn_idx]))
    
#     mutations = []
#     for c in candidate:    
#         word_idx, synonym = c
#         new_utt_tok = copy(triplet.utt_tok)    
#         new_utt_tok[word_idx] = synonym
#         new_utterance = " ".join(new_utt_tok)
#         mutations.append(MTriplet(triplet, utterance=new_utterance))
    
#     return mutations

# def us_en_substitute(triplet):
#     candidate = []

#     for key in us_en_synonym.keys():
#         if key in triplet.utt_tok:
#             word_idx = triplet.utt_tok.index(key)
#             subs_syn = us_en_synonym[key]
#             candidate.append((word_idx, subs_syn))


#     mutations = []
#     for c in candidate:    
#         word_idx, synonym = c
#         new_utt_tok = copy(triplet.utt_tok)    
#         new_utt_tok[word_idx] = synonym
#         new_utterance = " ".join(new_utt_tok)
#         mutations.append(MTriplet(triplet, utterance=new_utterance))
    
#     return mutations

def agg_substitute(triplet):
    agg_synonym = {
        "counting":  ["the number of", "the total number of", "the amount of"],
        "averaging": ["the average of", "the mean of"],
        "summation": ["the sum of", "the total sum of", "the amount of"], 
    }

    candidate = []
    for key in agg_synonym.keys():
        for i, synonym in enumerate(agg_synonym[key]):
            if synonym in triplet.utterance:
                start_idx = triplet.utterance.index(synonym)
                end_idx = start_idx + len(synonym)
                for subs_syn in agg_synonym[key]:
                    if subs_syn == synonym:continue
                candidate.append(triplet.utterance[:start_idx]+subs_syn+triplet.utterance[end_idx:])
    
    mutations = []
    for c in candidate:  
        mutations.append(MTriplet(triplet, utterance=c))
    
    return mutations


if __name__ == "__main__":
    dummy_schema = TSchema.dummy_schema("../../data/tables.json")
    triplet = Triplet("tell me the largest organization ?", dummy_schema, Query.dummy_query(dummy_schema))
    print(triplet.utterance)
    print(us_en_substitute(triplet).utterance)
    print(sup_substitute(triplet).utterance)