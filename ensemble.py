import sys, json
from eval import evaluate_one

decide_table = {
    "easy": 0,
    "medium": 0,
    "hard": 0,
    "extra": 1
}

result = []

with open(sys.argv[1]) as f:
    data = [line.strip().split("\t") for line in f.readlines() if line.strip() != ""]
    data = {d[0]:d for d in data}
    result.append(data)

with open(sys.argv[2]) as f:
    data = [line.strip().split("\t") for line in f.readlines() if line.strip() != ""]
    data = {d[0]:d for d in data}
    result.append(data)

with open(sys.argv[3]) as f:
    j = json.load(f)
    tables = {db["db_id"]:db for db in j}

ensemble_result = []
f=open("syntax-aug+ss", "w")
for k in result[0]:
    data_entry = result[0][k]
    e,p,h = evaluate_one(data_entry[1], data_entry[2], tables[data_entry[3]])
    if h=="extra":
        pred = result[1][k][2]
    else:
        pred = data_entry[2]
    f.write(f"{data_entry[0]}\t{data_entry[1]}\t{pred}\t{data_entry[3]}\t{data_entry[4]}\n")
f.close()
