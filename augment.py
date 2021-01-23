import json, sys
from tqdm import tqdm

from sampling.random_sampling import random_sampling
from sampling.stratiﬁed_sampling import stratified_sampling
from sampling.adaptive_sampling import adaptive_sampling_first, adaptive_sampling_second

assert sys.argv[1] in ["random", "stratified", "adaptive_first", "adaptive_second", "1", "2", "3", "4"]

try:
    train_file = sys.argv[2]
    tables_file = sys.argv[3]
    new_train_file = sys.argv[4]
    new_tables_file = sys.argv[5]
except:
    print("python augment.py [sample method] [synthetic_train_file] [synthetic_tables_file] [new_train_file] [new_tables_file] [new_dev_file (adaptive first) / method_dict (adaptive second)]")
    exit(0)

with open(train_file) as f:
    train = json.load(f)
with open(tables_file) as f:
    tables = json.load(f)
original_train = [i for i in train if "orig" in i["testcase"]]

print("sample from synthetic data\nmethod", sys.argv[1])
if sys.argv[1] in ["random", "1"]:
    sampled_train = random_sampling(train,len(original_train))
elif sys.argv[1] in ["stratified", "2"]:
    sampled_train = stratified_sampling(train,len(original_train))
elif sys.argv[1] in ["adaptive_first", "3"]:
    sampled_train, sampled_dev = adaptive_sampling_first(train)
    new_table = []
    tables = {d["db_id"]:d for d in tables}
    for t in sampled_train:
        new_table.append(tables[t["db_id"]])
    for t in sampled_dev:
        new_table.append(tables[t["db_id"]])
    print("dump to file")
    with open(new_train_file, "w") as f:
        json.dump(sampled_train, f)
    with open(new_tables_file, "w") as f:
        json.dump(new_table, f)
    with open(sys.argv[6], "w") as f:
        json.dump(sampled_dev, f)
    exit(0)
elif sys.argv[1] in ["adaptive_second", "4"]:
    with open(sys.argv[6]) as f:
        method_dict = json.load(f)
    sampled_train = adaptive_sampling_second(train, method_dict)
    new_table = []
    tables = {d["db_id"]:d for d in tables}
    method_count = {}
    for t in sampled_train:
        if t["method"] not in method_count: method_count[t["method"]] = 1
        else: method_count[t["method"]] += 1
        new_table.append(tables[t["db_id"]])
    for m in method_count:
        print(f"{m}: {method_count[m]}")
    with open(new_train_file, "w") as f:
        json.dump(sampled_train, f)
    with open(new_tables_file, "w") as f:
        json.dump(new_table, f)
    exit(0)
else:
    exit(1)


print(len(sampled_train))
# resolve table
new_tables = []
new_train = []
tables_dict = {d["db_id"]:d for d in tables}

print("insert original train")
for t in tqdm(original_train):
    new_tables.append(tables_dict[t["db_id"]])
    new_train.append(t)

print("insert sampled train")
for t in tqdm(sampled_train):
    new_tables.append(tables_dict[t["db_id"]])
    new_train.append(t)

print("dump to file")
with open(new_train_file, "w") as f:
    json.dump(new_train, f)
with open(new_tables_file, "w") as f:
    json.dump(new_tables, f)
