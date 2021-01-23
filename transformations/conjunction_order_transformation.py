import sys 
sys.path.append("..") 

import numpy as np


#from nlp_utils import spacy_doc
from Triplet import Triplet, MTriplet, Schema
from copy import copy, deepcopy

def conj_trans(triplet):
    if "and" not in triplet.utterance or "," not in triplet.utterance:
        return []
    # current linking algorithm may somehow fail
    try:
        linking_group, linking_label = triplet.tok_linking
    except:
        print("linking failed")
        return []
    candidates = []
    pointer = 0
    for i in range(len(linking_group)):
        curr_grp = linking_group[i]
        if len(curr_grp) == 1 and curr_grp[0] in ("and", ",") and pointer > 0 and pointer < len(linking_label) and linking_label[pointer-1] == "COL" and linking_label[pointer+1] == "COL":
            candidates.append((i-1, i+1))
        pointer += len(curr_grp)
    
    mutation = []

    for c in candidates:
        i, j = c

        def swap_grp(i,j):
            new_utt = ""
            for grp_idx in range(len(linking_group)):
                grp = linking_group[grp_idx]
                if grp_idx == i:
                    grp = linking_group[j]
                if grp_idx == j:
                    grp = linking_group[i]
                for tok in grp:
                    new_utt = new_utt + tok + " "
            return new_utt
        new_utt = swap_grp(i, j)
        mutation.append(MTriplet(triplet, utterance=new_utt))
    return mutation
