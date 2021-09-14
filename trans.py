
import pickle, json, time, copy
import numpy as np
from tqdm import tqdm

from transformations.prefix_transformation import prefix_insertion, prefix_removal, symmetric_prefix_substitution, asymmetric_prefix_substitution
from transformations.schema_column_mutation import column_insertion, column_remaning, column_removal
from transformations.schema_structual_transformation import normalization, flatten, opaque_key, col_shuffle, tab_shuffle
from transformations.underconstrained_synonym_transformation import sup_substitute, agg_substitute
from transformations.conjunction_order_transformation import conj_trans
from Triplet import Triplet, TSchema, Query
from multiprocessing import Pool

transformers = [
    prefix_insertion,
    prefix_removal,
    symmetric_prefix_substitution,
    column_insertion,
    column_remaning,
    column_removal,
    normalization,
    flatten,
    opaque_key,
    col_shuffle,  
    tab_shuffle,
    sup_substitute,
    agg_substitute, 
]

def transform(triplet, transformer_index):
    # check type
    assert isinstance(triplet, Triple)
    assert len(transformers) > transformer_index
    assert isinstance(transformers[transformer_index], callable)

    try:
        return transformers[transformer_index](triplet)
    except:
        return None

def exhausive_transform(triplet):
    mutations = []
    for t in transformers:
        try:
            start = time.time()
            mutation = t(triplet)
            # print(t, time.time()-start)
            if isinstance(mutation, list): 
                for i, m in enumerate(mutation):
                    if i>=10 and "prefix" in t.__name__:break
                    m.method = t.__name__
                    mutations.append(m)
            else: 
                mutation.method = t.__name__
                mutations.append(mutation)
        except AssertionError as e:
            # print(t, time.time()-start)
            pass
    return mutations

if __name__ == "__main__":
    start = time.time()

    f = open("data/tables.json")
    j = json.load(f)
    raw_tables = {i["db_id"]:i for i in j}

    data, tables = [], []
    f = open("data/train_spider.json")
    dev = json.load(f)
    # dev = np.random.choice(dev, size=200)

    def constrcut_and_mutate(json_entry):
        q_tok = json_entry["query_toks"]
        q_tok_wo_val = json_entry["query_toks_no_value"]
        if json_entry["db_id"] not in raw_tables: 
            print("table not found", json_entry["db_id"])
            return []
        table = raw_tables[json_entry["db_id"]]
        schema = TSchema.construct_schema_by_json(table)
        query = json_entry["query"]
        query = Query(query, schema)
        triplet = Triplet(json_entry["question"], schema, query)
        return exhausive_transform(triplet)

    mutations = []
    count = 0
    for i in tqdm(range(len(dev))):
        # print(dev[i]["db_id"])
        mutations.append((constrcut_and_mutate(dev[i]), dev[i], i))
        count += len(mutations[-1][0])
        # print(f"{i+1}/{len(dev)}")
        # print(f"#mutation: {count}")
    
    def convert2json(entry):
        m, o, idx = entry
        data = []
        o["testcase"] = str(idx) + "__orig"
        o["method"] = "seed"
        data.append([o, raw_tables[o["db_id"]]])
        for j, mutation in enumerate(m):
            try:
                m_j, t_j = mutation.export_spider_json()
            except:
                continue
            m_j["testcase"] = str(idx) + "__" + str(j)
            m_j["method"] = mutation.method if mutation.method else ""
            m_j["query"] = o["query"]
            m_j["query_toks"] = o["query_toks"]
            m_j["query_toks_no_value"] = o["query_toks_no_value"]
            schema = TSchema.construct_schema_by_json(t_j)
            query = Query(m_j["query"], schema)
            m_j["sql"] = query.sql_label
            data.append([m_j, t_j])
        return data

    print("export json")
    jsons = []
    for i in tqdm(mutations):
        x=convert2json(i)
        jsons.append(x)
    
    reduced_data = []
    for j in jsons:
        reduced_data += j

    print("resolve duplicated db_id")
    db_ids = set()
    resolved_data = []
    resolved_table = []
    
    for i in range(len(reduced_data)):
        db_id = reduced_data[i][0]["db_id"]
        prefix = db_id if "__TEQL__" not in db_id else db_id.split("__TEQL__")[0]
        idx = 0
        while db_id in db_ids:
            db_id = prefix + "__TEQL__" + str(idx)
            idx+=1

        temp_table = copy.deepcopy(reduced_data[i][1])
        temp_table["db_id"] = db_id
        resolved_table.append(temp_table)
        temp_data = copy.deepcopy(reduced_data[i][0])
        
        temp_data["db_id"] = db_id
        resolved_data.append(temp_data)
        db_ids.add(db_id)

    
    print("#testcase:", len(reduced_data))
    print("process time:", time.time()-start)

    print([i["testcase"] for i in resolved_data if "orig" in i["testcase"] ])

    with open("mutation/train.json", "w") as f:
        json.dump(resolved_data, f, indent=2)
    with open("mutation/train-tables.json", "w") as f:
        json.dump(resolved_table, f, indent=2)