import sys 
sys.path.append("..") 

import numpy as np


#from nlp_utils import spacy_doc
from Triplet import Triplet, MTriplet, Schema, Query
from copy import copy, deepcopy
try:
    from trans_utils import _random_choice
except:
    from transformations.trans_utils import _random_choice 

def normalization(triplet):

    candidates = []
    schema = deepcopy(triplet.schema)

    for col in schema.columns:
        if len(candidates) >= 10:break
        if "*" in col["name"]: continue
        if col["is_foreign_key"] is True or col["is_primary_key"] is True:
            continue
        if col["name_original"].lower() in triplet.sql.sql.lower():
            continue
        candidates.append(col)
    

    mutations = []
    for col in candidates:
        schema = deepcopy(triplet.schema)

        schema.tables.append(col["name"])
        schema.original_tables.append(col["name_original"])

        new_tab_idx = schema.tables.index(col["name"])

        linking_col_orig_tab = copy(col)
        linking_col_ref_tab = copy(col)

        schema.columns.append(linking_col_orig_tab)
        schema.columns.append(linking_col_ref_tab)
        
        orig_col_idx = schema.columns.index(linking_col_orig_tab)
        ref_col_idx = schema.columns.index(linking_col_ref_tab)

        schema.primary_key.append(ref_col_idx)
        schema.foreign_key.append([orig_col_idx, ref_col_idx])

        linking_col_orig_tab["name"] = linking_col_orig_tab["name"] + " id"
        linking_col_orig_tab["name_original"] = linking_col_orig_tab["name_original"] + "_id"
        linking_col_orig_tab["type"] = "number"
        linking_col_orig_tab["is_foreign_key"] = True 
        linking_col_orig_tab["is_primary_key"] = False 
        linking_col_orig_tab["foreign_keys"] = [orig_col_idx, ref_col_idx] 
        linking_col_orig_tab["table_idx"] 

        linking_col_ref_tab["name"] = linking_col_ref_tab["name"] + " id"
        linking_col_ref_tab["name_original"] = linking_col_ref_tab["name_original"] + "_id"
        linking_col_ref_tab["type"] = "number"
        linking_col_ref_tab["is_foreign_key"] = True 
        linking_col_ref_tab["is_primary_key"] = True 
        linking_col_ref_tab["foreign_keys"] = [orig_col_idx, ref_col_idx] 
        linking_col_ref_tab["table_idx"] = new_tab_idx

        col["table_idx"] = new_tab_idx
        mutations.append(MTriplet(triplet, schema=schema, sql=Query(triplet.sql.sql, schema )))
    
    return mutations

# table joining
def flatten(triplet):
    candidates = []

    schema = deepcopy(triplet.schema)

    for i, fks in enumerate(schema.foreign_key):
        if len(candidates) >= 10:break
        if len(fks) != 2: continue
        
        fk = [k for k in fks if not schema.columns[k]["is_primary_key"]]
        if len(fk) == 0: continue
        fk = fk[0]
        pk = [k for k in fks if schema.columns[k]["is_primary_key"]]
        if len(pk) == 0: continue
        pk = pk[0]
        ref_tab = schema.columns[pk]["table_idx"]
        referee_tab = schema.columns[fk]["table_idx"]
        if schema.original_tables[ref_tab].lower() in triplet.sql.sql.lower():
            continue
        candidates.append((fk, pk, i))
    
    mutations = []
    for candidate in candidates:
        schema = deepcopy(triplet.schema)
        fk, pk, i = candidate
        # rm from foreign key list
        schema.foreign_key.pop(i)
        idx = schema.primary_key.index(pk)
        schema.primary_key.pop(idx)
        fk_col, pk_col = schema.columns[fk], schema.columns[pk]

        ref_tab = schema.columns[pk]["table_idx"]
        ref_cols = [col for col in schema.columns if col["table_idx"] == ref_tab and not col["is_primary_key"]]

        referer_tab = schema.columns[fk]["table_idx"]
        referer_tab_name = schema.tables[ref_tab]
        referer_tab_original_name = schema.original_tables[ref_tab]

        for ref_col in ref_cols:
            if referer_tab_name not in ref_col["name"]:
                ref_col["name"] = referer_tab_name + " " + ref_col["name"]  if referer_tab_name not in ref_col["name"] else ref_col["name"]
                ref_col["name_original"] = referer_tab_name + "_" + ref_col["name_original"] if referer_tab_name not in ref_col["name_original"] else ref_col["name_original"]
            ref_col["table_idx"] = referer_tab
        
        schema.tables.pop(ref_tab)
        schema.original_tables.pop(ref_tab)
        schema.columns.pop(pk)
        # lift col index
        for fks in schema.foreign_key:
            for j in range(len(fks)):
                if fks[j] > pk: fks[j] -= 1
        for i in range(len(schema.primary_key)):
            if schema.primary_key[i] > pk: schema.primary_key[i] -= 1
        for i in range(len(schema.columns)):
            if schema.columns[i]["table_idx"] > ref_tab: 
                schema.columns[i]["table_idx"] -= 1
        
        def swap_col(i, j):
            col_i = deepcopy(schema.columns[i])
            col_j = deepcopy(schema.columns[j])
            schema.columns[i] = col_j
            schema.columns[j] = col_i

            for k in range(len(schema.primary_key)):
                if schema.primary_key[k] == i: 
                    schema.primary_key[k] = j
                elif schema.primary_key[k] == j:
                    schema.primary_key[k] = i

            for k1 in range(len(schema.foreign_key)):
                for k2 in range(len(schema.foreign_key[k1])):
                    if schema.foreign_key[k1][k2] == i:
                        schema.foreign_key[k1][k2] = j
                    elif schema.foreign_key[k1][k2] == j:
                        schema.foreign_key[k1][k2] = i
        
        # sort column by tab idx
        for i in range(len(schema.columns)):
            for j in range(i+1, len(schema.columns)):
                if schema.columns[i]["table_idx"] > schema.columns[j]["table_idx"]:
                    swap_col(i, j)
        
        mutations.append(MTriplet(triplet, schema=schema, sql=Query(triplet.sql.sql, schema )))
    return mutations

def opaque_key(triplet):
    candidates = deepcopy(triplet.schema.foreign_key)[:10]

    mutations = []
    for c in candidates:
        schema = deepcopy(triplet.schema)
        schema.foreign_key.remove(c)
        mutations.append(MTriplet(triplet, schema=schema, sql=Query(triplet.sql.sql, schema)))
    return mutations

def col_shuffle(triplet):

    schema = deepcopy(triplet.schema)
    tab2col = {}
    for i in range(len(triplet.schema.columns)):
        if triplet.schema.columns[i]["table_idx"] == -1: continue
        if triplet.schema.columns[i]["table_idx"] not in tab2col:
            tab2col[triplet.schema.columns[i]["table_idx"]] = [i]
        else:
            tab2col[triplet.schema.columns[i]["table_idx"]].append(i)
    
    tab2col = {k: tab2col[k] for k in tab2col if len(tab2col[k])>1}
    candidates = []
    for i in range(len(schema.columns)//3):
        if len(candidates) > 10: break
        tab_idx = [k for k in tab2col]
        shuf_tab = _random_choice(tab_idx)
        i = _random_choice(tab2col[shuf_tab])
        j = _random_choice(tab2col[shuf_tab], i)
        if (i,j) not in candidates and (j,i) not in candidates: candidates.append((i,j))
    mutations = []
    for c in candidates:
        schema = deepcopy(triplet.schema)
        i, j = c
        def swap_col(i, j):
            col_i = deepcopy(schema.columns[i])
            col_j = deepcopy(schema.columns[j])
            schema.columns[i] = col_j
            schema.columns[j] = col_i

            for k in range(len(schema.primary_key)):
                if schema.primary_key[k] == i: 
                    schema.primary_key[k] = j
                elif schema.primary_key[k] == j:
                    schema.primary_key[k] = i

            for k1 in range(len(schema.foreign_key)):
                for k2 in range(len(schema.foreign_key[k1])):
                    if schema.foreign_key[k1][k2] == i:
                        schema.foreign_key[k1][k2] = j
                    elif schema.foreign_key[k1][k2] == j:
                        schema.foreign_key[k1][k2] = i
        swap_col(i ,j)
        mutations.append(MTriplet(triplet, schema=schema, sql=Query(triplet.sql.sql, schema)))
    return mutations

def tab_shuffle(triplet):
    schema = deepcopy(triplet.schema)
    tab_num = len(schema.tables)
    tab_ids = list(range(tab_num))

    candidates = []
    for i in range(int(tab_num/1.5)):
        tab_i = _random_choice(tab_ids)
        tab_j = _random_choice(tab_ids, tab_i)
        if (tab_i, tab_j) not in candidates and (tab_j, tab_i) not in candidates:
            candidates.append((tab_i, tab_j))
    
    mutations = []
    for c in candidates:
        i,j = c

        schema = deepcopy(triplet.schema)
        for k in range(len(schema.columns)):
            if schema.columns[k]["table_idx"] == i:
                schema.columns[k]["table_idx"] = j
            elif schema.columns[k]["table_idx"] == j:
                schema.columns[k]["table_idx"] = i
        schema.tables[i], schema.tables[j] = schema.tables[j], schema.tables[i]
        schema.original_tables[i], schema.original_tables[j] = schema.original_tables[j], schema.original_tables[i]

        def swap_col(i, j):
            col_i = deepcopy(schema.columns[i])
            col_j = deepcopy(schema.columns[j])
            schema.columns[i] = col_j
            schema.columns[j] = col_i

            for k in range(len(schema.primary_key)):
                if schema.primary_key[k] == i: 
                    schema.primary_key[k] = j
                elif schema.primary_key[k] == j:
                    schema.primary_key[k] = i

            for k1 in range(len(schema.foreign_key)):
                for k2 in range(len(schema.foreign_key[k1])):
                    if schema.foreign_key[k1][k2] == i:
                        schema.foreign_key[k1][k2] = j
                    elif schema.foreign_key[k1][k2] == j:
                        schema.foreign_key[k1][k2] = i
        
        # sort column by tab idx
        for i in range(len(schema.columns)):
            for j in range(i+1, len(schema.columns)):
                if schema.columns[i]["table_idx"] > schema.columns[j]["table_idx"]:
                    swap_col(i, j)
        mutations.append(MTriplet(triplet, schema=schema, sql=Query(triplet.sql.sql, schema)))
    return mutations
