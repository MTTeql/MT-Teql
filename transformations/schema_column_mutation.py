import sys 
sys.path.append("..") 

import numpy as np


#from nlp_utils import spacy_doc
from Triplet import Triplet, MTriplet, Schema
try:
    from trans_utils import has_a, synonym, _random_choice
except:
    from transformations.trans_utils import has_a, synonym, _random_choice
from copy import copy, deepcopy


def column_insertion(triplet):
    schema = deepcopy(triplet.schema)
    candidate = []
    for tab_idx, tab_name in enumerate(schema.tables):
        if len(candidate) >= 10:break
        tab_has_a = has_a(tab_name)
        for has_a_item in tab_has_a:
            if schema.exists(has_a_item): continue
            if has_a_item in triplet.utt_tok: continue
            candidate.append((tab_idx, has_a_item))
        
    mutations = []
    for i in candidate:
        schema = deepcopy(triplet.schema)
        tab_idx, col_name = i
        new_col = {}
        new_col["table_idx"] = tab_idx
        new_col["name"] = col_name
        new_col["name_original"] = col_name
        new_col["type"] = _random_choice(["text", "number"])
        new_col["is_foreign_key"] = False 
        new_col["foreign_keys"] = []
        new_col["is_primary_key"] = False
        schema.columns.append(new_col)
        mutations.append(MTriplet(triplet, schema=schema))

    return mutations

def column_remaning(triplet):
    schema = deepcopy(triplet.schema)
    candidate = []
    for col_idx, col in enumerate(schema.columns):
        if len(candidate) >= 10:break
        if "_" in col["name_original"] or "*" in col["name"]: continue
        if col["is_foreign_key"] is True or col["is_primary_key"] is True: continue
        if col["name_original"].lower() in triplet.sql.sql.lower(): continue
        col_synonym = synonym(col["name"])
        for col_synonym_item in col_synonym:
            candidate.append((col_idx, col_synonym_item))
    
    mutations = []
    for i in candidate:
        schema = deepcopy(triplet.schema)
        col_idx, col_synonym_item = i
        schema.columns[col_idx]["name"] = col_synonym_item
        schema.columns[col_idx]["name_original"] = col_synonym_item
        mutations.append(MTriplet(triplet, schema=schema))

    return mutations

def column_removal(triplet):
    schema = deepcopy(triplet.schema)
    candidate = []
    for col_idx, col in enumerate(schema.columns):
        if len(candidate) >= 10:break
        if "*" in col["name"]: continue
        if col["is_foreign_key"] is True or col["is_primary_key"] is True: continue
        if col["name_original"].lower() in triplet.sql.sql.lower(): continue
        candidate.append(col_idx)
    
    mutations = []
    for i in candidate:
        schema = deepcopy(triplet.schema)
        col_idx = i
        schema.columns.pop(col_idx)
        for k in range(len(schema.foreign_key)):
            for j in range(len(schema.foreign_key[k])):
                if schema.foreign_key[k][j] > col_idx:
                    schema.foreign_key[k][j] -= 1
        for k in range(len(schema.primary_key)):
            if schema.primary_key[k] > col_idx:
                schema.primary_key[k] -= 1
        mutations.append(MTriplet(triplet, schema=schema))

    return mutations