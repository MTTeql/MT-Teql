import json, os, Triplet, tqdm

path = "../mutation/microbenchmark"

utterance_files = [os.path.join(path, f) for f in os.listdir(path) if ".txt" in f]

utterances = {}
for filename in utterance_files:
    with open(filename) as f:
        curr_utterance = [l.strip() for l in f.readlines() if l.strip() != ""]
    method = os.path.basename(filename)
    method = method[:method.index(".txt")]
    utterances[method] = curr_utterance

with open(os.path.join(path, "gold.sql")) as f:
    sql = [l.strip()[:-1] for l in f.readlines() if l.strip() != ""]

with open(os.path.join(path, "tables.json")) as f:
    tab = json.load(f)[0]
    schema = Triplet.TSchema.construct_schema_by_json(tab)

dev = []
for i in tqdm.tqdm(range(57)):
    query = Triplet.Query(sql[i], schema)
    for j, method in enumerate(utterances):
        curr_utterance = utterances[method][i]
        triplet = Triplet.Triplet(curr_utterance, schema, query)
        triplet_json = triplet.spider_like_json
        if method == "naive_source":
            triplet_json["testcase"] = str(i) + "__orig"
            triplet_json["method"] = "seed"
        else:
            triplet_json["testcase"] = str(i) + "__" + str(j)
            triplet_json["method"] = method
        dev.append(triplet_json)

with open(os.path.join(path, "dev.json"), "w") as f:
    json.dump(dev,f, indent=2)
