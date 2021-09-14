import json, copy

from ir.spider_parse_one import get_one_schema_from_json
from ir.spider_parse_one import Schema
from ir.process_sql import get_sql, tokenize
from ir.sql2IR import Parser
from ir.data_preprocess import process_one

class Triplet:
    def __init__(self, utterance: str, schema: "TSchema", sql: "Query"):
        self.utterance = utterance
        self.schema = schema
        self.sql = sql
        # compute on-demmand
        self._dep_tree = None
        self._tok = None
        self._ir = None
        self._augmented_data = None

    @property
    def dep_tree(self):
        if self._dep_tree is None:
            from nlp_utils import dependency_parsing
            self._dep_tree = dependency_parsing(self.utterance)
        return self._dep_tree
    
    @property
    def utt_tok(self):
        if self._tok is None:
            from nlp_utils import spacy_doc
            self._tok = [t.text for t in spacy_doc(self.utterance)]
        return self._tok

    @property
    def tok_linking(self):
        data = self.spider_like_json
        table = self.schema.export()
        if self._augmented_data is None:
            augmented_data = process_one(data, table)
        else:
            augmented_data = self._augmented_data
        tok_link_rlt = []
        for i, toks in enumerate(augmented_data["question_arg"]):
            for tok in toks:
                tok_link_rlt.append(augmented_data["question_arg_type"][i][0].upper())
        return augmented_data["question_arg"],  tok_link_rlt

    @property
    def spider_like_json(self):
        json_entry = {}
        json_entry["db_id"] = self.schema.db_id
        json_entry["question"] = self.utterance
        json_entry["question_toks"] = self.utt_tok
        json_entry["query"] = self.sql.sql
        json_entry["query_toks"] = tokenize(self.sql.sql)
        json_entry["query_toks_no_value"] = copy.copy(json_entry["query_toks"])
        for i in range(len(json_entry["query_toks_no_value"])):
            if "__val_" in json_entry["query_toks_no_value"][i]:
                json_entry["query_toks_no_value"][i] = "value"
            try:
                float(json_entry["query_toks_no_value"][i])
                json_entry["query_toks_no_value"][i] = "value"
            except:
                pass
        json_entry["sql"] = self.sql.sql_label
        return json_entry

    def sem_ir(self, parser):
        if self._augmented_data is None:
            augmented_data = process_one(data, table)
        else:
            augmented_data = self._augmented_data
        return parser.full_parse(augmented_data)
    
    @staticmethod
    def export_full_spider_json(triplets, folder=None):
        data = [] 
        tables = []
        db_id = set()

        for t in triplets:
            tab = t.schema.export()
            if tab["db_id"] not in db_id:
                tab["db_id"] = tab["db_id"] + "_TEQL1"
            while tab["db_id"] in db_id:
                tab["db_id"] = tab["db_id"].split("_TEQL")[0] + "_TEQL" + str(int(tab["db_id"].split("_TEQL")[1])+1)
            tables.append(tab)

            inst = t.spider_like_json
            inst["db_id"] = tab["db_id"]
            data.append(inst)
        return data, tables
        # with open(os.path.join(folder, "dev.json"), 'w') as f:
        #     json.dump(data, f)

        # with open(os.path.join(folder, "tables.json"), 'w') as f:
        #     json.dump(tables, f)

    def __str__(self):
        s = "Utterance: " + self.utterance + "\n"
        s+= "Schema   : " + self.schema.db_id + "\n"
        s+= "SQL Query: " + self.sql.sql
        return s

class MTriplet(Triplet):
    def __init__(self, original_triplet: "Triplet", utterance: str = None, schema: "Schema" = None, sql: "Query" = None, method=""):
        assert utterance is not None or schema is not None or sql is not None
        self.utterance = utterance if utterance is not None else original_triplet.utterance
        self.schema = schema if schema is not None else original_triplet.schema
        if sql is not None:
            self.sql = sql
        elif schema is not None:
            self.sql = Query(original_triplet.sql.sql, schema)
        else:
            self.sql = original_triplet.sql
        self.original_triplet = original_triplet
        # compute on-demmand
        self._dep_tree = None
        self._tok = None
        self._ir = None
        self._augmented_data = None
        self.method = None
        
    def __str__(self):
        s = "Original Triplet:\n" + str(self.original_triplet) + "\n"
        s+= "New Triplet:\n"
        s+= "Utterance: " + self.utterance + "\n"
        s+= "Schema   : " + self.schema.db_id + "\n"
        s+= "SQL Query: " + self.sql.sql
        return s
    
    def export_spider_json(self, db_ids=None):

        tab = self.schema.export()
        inst = self.spider_like_json

        return inst, tab

class TSchema:
    def __init__(self, db_id, tables, original_tables, columns, primary_key, foreign_key):
        self.db_id = db_id
        self.tables = tables
        self.original_tables = original_tables
        self.columns = columns
        self.primary_key = primary_key
        self.foreign_key = foreign_key

    def exists(self, word):
        for col in self.columns:
            if word.lower() in col["name"].lower(): return True
            if col["name"].lower() in word.lower(): return True
        for tab in self.tables:
            if word.lower() in tab.lower(): return True
            if tab.lower() in word.lower(): return True
        return False
    
    def get_columns_by_table(self, table_idx=None, table_name=None):
        if table_idx is None and table_name is None:
            return []
        if table_idx is not None:
            return [col for col in self.columns if col["table_idx"] == table_idx]
        if table_name is not None:
            return [col for col in self.columns if self.tables[col["table_idx"]] == table_name]

    @staticmethod
    def process_columns(json_entry): 
        columns = []
        for i, col_name in enumerate(json_entry["column_names"]):
            col = {}
            col["table_idx"] = col_name[0]
            col["name"] = col_name[1]
            col["name_original"] = json_entry["column_names_original"][i][1]
            col["type"] = json_entry["column_types"][i]
            col["is_foreign_key"] = False 
            col["foreign_keys"] = []
            for fk in json_entry["foreign_keys"]:
                if i in fk:
                    col["is_foreign_key"] = True 
                    col["foreign_keys"] = fk
            col["is_primary_key"] = True if i in json_entry["primary_keys"] else False
            columns.append(col)
            
        return columns

    @staticmethod
    def construct_schema_by_json(json_entry):
        db_id = json_entry["db_id"]
        tables = json_entry["table_names"]
        original_tables = json_entry["table_names_original"]
        columns = TSchema.process_columns(json_entry)
        primary_key = json_entry["primary_keys"]
        foreign_key = json_entry["foreign_keys"]
        return TSchema(db_id, tables, original_tables, columns, primary_key, foreign_key)
    
    @staticmethod
    def dummy_schema(tab_file):
        f = open(tab_file)
        j = json.load(f)
        return TSchema.construct_schema_by_json(j[0])
    
    def export(self):
        json_entry = {}
        json_entry['db_id'] = self.db_id
        json_entry['column_names_original'] = [[col["table_idx"], col["name_original"]] for col in self.columns]
        json_entry['column_names'] = [[col["table_idx"], col["name"]] for col in self.columns]
        json_entry['column_types'] = [col["type"] for col in self.columns]
        json_entry["table_names"] = self.tables
        json_entry["table_names_original"] = self.original_tables
        json_entry["primary_keys"] = self.primary_key
        json_entry["foreign_keys"] = self.foreign_key
        return json_entry

class Query:
    def __init__(self, sql:str, schema):
        self.sql = sql
        self.schema = schema
        self._sql_label = None
        self._ir = None
    
    @property
    def sql_label(self):
        json_entry = self.schema.export()
        inner_schema = get_one_schema_from_json(json_entry)
        self._sql_label = get_sql(inner_schema, self.sql)
        return self._sql_label
    
    # TODO
    @property
    def tok_no_val(self):
        pass
    
    @staticmethod
    def dummy_query(schema):
        col = schema.columns[1]
        tab = schema.tables[col["table_idx"]]
        sql = "SELECT " + col["name_original"] + " FROM " + tab
        return Query(sql, schema)
    
if __name__ == "__main__":
    import sys
    from transformations.conjunction_order_transformation import conj_trans
    f = open(sys.argv[1])
    data = json.load(f)[0]
    f = open(sys.argv[2])
    tab = json.load(f)
    tab = [t for t in tab if t["db_id"]==data["db_id"]][0]
    schema = TSchema.construct_schema_by_json(tab)
    query = Query(data["query"], schema)
    triplet = Triplet("what is the song name, age and country of singers ", schema, query)
    for m in conj_trans(triplet):
        print(m)