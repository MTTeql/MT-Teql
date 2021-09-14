import sys 
sys.path.append("..") 

import numpy as np

#from nlp_utils import spacy_doc
from Triplet import Triplet, MTriplet
try:
    from trans_utils import _random_choice
except:
    from transformations.trans_utils import _random_choice

def prefix_insertion(triplet):
    # defined common prefix
    interrogative_prefix = ["what", "which ", "where ", "when ", "how "]
    # declarative prefix can insert before interrogative prefix and substitute it.
    declarative_prefix = ["tell me ", "let me know ", "find ", "return me ", "return ", "list ", "show me ", "show ", "give me ", "give "]

    insertable = False
    for prefix in interrogative_prefix:
        if triplet.utterance.lower().find(prefix) == 0:
            insertable = True 
            break
    
    assert insertable

    mutations = [MTriplet(triplet, utterance= p + triplet.utterance.lower()) for p in declarative_prefix]
    return mutations

def prefix_removal(triplet):
    # defined common prefix
    interrogative_prefix = ["what is "]
    # declarative prefix can insert before interrogative prefix and substitute it.
    declarative_prefix = ["tell me ", "let me know ", "find ", "return me ", "return ", "list ", "show me ", "show ", "give me ", "give "]

    removable = False
    for prefix in interrogative_prefix:
        if triplet.utterance.lower().find(prefix) == 0:
            removable = prefix 
            break
    
    assert removable

    new_utterance = triplet.utterance
    new_utterance = new_utterance[len(removable):]

    return MTriplet(triplet, utterance= new_utterance)

def symmetric_prefix_substitution(triplet):
    # defined common prefix
    interrogative_prefix = ["what is ", "what's ", "what are ", "what're ", "which is ", "which "]
    special_interrogative_prefix = ["where", "when"]
    # declarative prefix can insert before interrogative prefix and substitute it.
    declarative_prefix = ["tell me ", "let me know ", "find ", "return me ", "return ", 
    "list ", "show me ", "show ", "give me ", "give "]
    # greedy match "xxx all" before match "xxx"
    # declarative_prefix = [i + "all " for i in declarative_prefix] + declarative_prefix
    common_prefix = interrogative_prefix + declarative_prefix
    counting_prefix = ["how many ", "count "]

    substitution = False
    for prefix in common_prefix:
        if triplet.utterance.lower().find(prefix) == 0:
            if prefix in declarative_prefix:
                for int_prefix in interrogative_prefix:
                    assert int_prefix not in triplet.utterance
            substitution = prefix 
            break
    
    for prefix in counting_prefix:
        if triplet.utterance.lower().find(prefix) == 0:
            substitution = prefix 
            break
    
    assert substitution
    new_utterance = triplet.utterance.lower()
    new_utterance = new_utterance[len(substitution):]
    candidates = common_prefix if substitution in common_prefix else counting_prefix
    candidates.remove(substitution)

    return [MTriplet(triplet, utterance= new_prefix + new_utterance) for new_prefix in candidates]

def asymmetric_prefix_substitution(triplet):

    # defined common prefix
    interrogative_prefix = ["what is ", "what's ", "what are ", "what're ", "which is ", "which "]
    special_interrogative_prefix = ["where", "when"]
    # declarative prefix can insert before interrogative prefix and substitute it.
    declarative_prefix = ["tell me ", "let me know ", "find ", "return me ", "return ", 
    "list ", "show me ", "show ", "give me ", "give "]
    # greedy match "xxx all" before match "xxx"
    # declarative_prefix = [i + "all " for i in declarative_prefix] + declarative_prefix
    common_prefix = interrogative_prefix + declarative_prefix

    asymmetric_symbol = {
        "where ": ["the place of ", "the location of ", "the country of ", "the city of "],
        "when ": ["the time of ", "the date of ","the year of "],
        "how many ": ["the number of ", "the amount of ", "the total number of "]
    }

    substitution = False
    for prefix in common_prefix:
        if triplet.utterance.find(prefix) != 0: continue

        for key in asymmetric_symbol.keys():
            for query_prefix in asymmetric_symbol[key]:
                if triplet.utterance.lower().find(prefix + query_prefix) == 0:
                    substitution = (key, prefix + query_prefix)
                    break
            if substitution: break
        if substitution: break
    
    assert substitution

    new_utterance = triplet.utterance.lower()
    new_utterance = new_utterance[len(substitution[1]):]
    new_prefix = substitution[0]

    return MTriplet(triplet, utterance= new_prefix + new_utterance)


# def prefix_transformation(triplet):
#     utterance = triplet.utterance
#     # check sentence number
#     # raise exception if more than one sentence
#     # assert len(list(doc.sents)) == 1

#     # defined common prefix
#     interrogative_prefix = ["what is ", "what's ", "what are ", "what're ", "which is ", "which "]
#     special_interrogative_prefix = ["where", "when"]
#     # declarative prefix can insert before interrogative prefix and substitute it.
#     declarative_prefix = ["tell me ", "let me know ", "find ", "return me ", "return ", 
#     "list ", "show me ", "show ", "give me ", "give "]
#     # greedy match "xxx all" before match "xxx"
#     # declarative_prefix = [i + "all " for i in declarative_prefix] + declarative_prefix
#     common_prefix = interrogative_prefix + declarative_prefix

#     # defined prefix transformation rules
#     extend_prefix = lambda prefix, suffix: [i + suffix for i in prefix]

#     symmetric_prefix = {
#         "common_prefix": common_prefix,
#         "counting_prefix": ["how many ", "count "],
#     }

#     asymmetric_symbol = {
#         "where ": ["the place of ", "the location of ", "the country of ", "the city of "],
#         "when ": ["the time of ", "the date of ","the year of "]
#     }

#     # if asymmetric transformation is available, perform it first
#     # asymmetric transformation*
#     is_asymmetric = False
#     for key in asymmetric_symbol.keys():
#         key_flag = False
#         for symb in asymmetric_symbol[key]:
#             symb_flag = False
#             for prefix in common_prefix:
#                 if utterance.find(prefix+symb) == 0:
#                     query_entry = utterance[len(prefix+symb):]
#                     utterance = key + query_entry
#                     symb_flag = True
#                     key_flag = True
#                     is_asymmetric = True
#                     break
#             if symb_flag: break
#         if key_flag: break
#     # if asymmetric transformation, other transformation is no longer available except perfix insertion
#     # decide whether insert prefix
#     if is_asymmetric:
#         if round(np.random.rand()) == 0:
#             prefix = np.random.choice(declarative_prefix)
#             utterance = prefix + utterance
#     else:
#         # form transformation, symmetric prefix transformation
#         # prefix insertion
#         is_symmetric = False
#         is_counting = False
#         for key in symmetric_prefix.keys():
#             key_flag = False
#             for prefix in symmetric_prefix[key]:
#                 if utterance.find(prefix) == 0:
#                     # check if is counting prefix
#                     if key == "counting_prefix": 
#                         is_counting = True
#                         if np.random.rand() < .7 : break
#                     # choose another prefix
#                     query_entry = utterance[len(prefix):]
#                     new_prefix = np.random.choice(symmetric_prefix[key])
#                     while new_prefix == prefix: 
#                         new_prefix = np.random.choice(symmetric_prefix[key])
#                     utterance = new_prefix + query_entry
#                     key_flag = True 
#                     is_symmetric = True
                    
#                     break
#             if is_symmetric: break

#         # decide whether to insert prefix
#         is_insertion = False
#         if round(np.random.rand()) == 0 or is_counting:
#             for prefix in interrogative_prefix + ["how many"]:
#                 if utterance.find(prefix) == 0:
#                     new_prefix = np.random.choice(declarative_prefix)
#                     utterance = new_prefix + utterance
#                     is_insertion = True 
#                     break
    
#     # punctuation correction
#     is_corrected = False
#     for prefix in ["what", "which", "how"]:
#         if utterance.find(prefix) == 0:
#             if utterance[-1] == ".": utterance = utterance[:-1] + "?"
#             elif utterance[-1] == "?": pass 
#             else: utterance = utterance + "?"
#             is_corrected = True
#             break
#     if not is_corrected:
#         if utterance[-1] == "?": utterance = utterance[:-1] + "."
#         elif utterance[-1] == ".": pass 
#         else: utterance = utterance + "."
#         is_corrected = True
    
#     assert (is_asymmetric or is_symmetric or is_insertion) and is_corrected
#     return MTriplet(triplet, utterance=utterance)


if __name__ == "__main__":
    triplet = Triplet("how many buttercup kitchen are there in san francisco ?", "", "")
    for i in range(100):
        try:
            print(prefix_transformation(triplet).utterance)
        except Exception as e:
            print(e)