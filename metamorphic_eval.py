from eval import evaluate_one
import argparse, json, copy, time

from multiprocessing import Pool

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', dest='output', type=str)
    parser.add_argument('-t', '--table', dest='table', type=str)
    args = parser.parse_args()


    tables = args.table
    with open(tables) as f:
        j = json.load(f)
    tables = {db["db_id"]:db for db in j}

    output = args.output
    with open(output) as f:
        data = [line.strip().split("\t") for line in f.readlines() if line.strip() != ""]
    print(len([d for d in data if "orig" in d[0]]))
    
    def evaluate(data_entry):
        return (data_entry[0], evaluate_one(data_entry[1], data_entry[2], tables[data_entry[3]]), data_entry[4])
    
    with Pool(processes=24) as pool:
        results = pool.map(evaluate, data)
    
    testcase_dict = {}
    for i, rlt in enumerate(results):
        testcase, score, _ = rlt

        if "orig" in testcase:
            testcase_dict[testcase.split("__")[0]] = (i, score[0], score[2])
    
    hardness_stat = {'easy':[0,0], 'medium':[0,0], 'hard':[0,0], 'extra':[0,0], 'all':[0,0], "unknown": [0,0]}
    method_stat = {}
    method_acc_stat = {}
    ood_stat = {"orig": copy.deepcopy(hardness_stat)}

    for i, rlt in enumerate(results):
        testcase, score, method = rlt
        if "orig" not in testcase:
            idx = testcase.split("__")[0]
            if idx in testcase_dict:
                orig_idx, orig_score, _ = testcase_dict[idx]

                hardness_stat[_][1] += 1
                hardness_stat["all"][1] += 1

                if method not in method_stat:
                    method_stat[method] = [0,1]
                    method_acc_stat[method] = [0,1]
                else:
                    method_stat[method][1] += 1
                    method_acc_stat[method] = [0,1]
                if score[0] == 1:
                    method_acc_stat[method][0] += 1
                if score[0] != orig_score: 
                    hardness_stat[_][0] += 1
                    hardness_stat["all"][0] += 1
                    method_stat[method][0] += 1

    for k in hardness_stat:
        if hardness_stat[k][1] != 0:
            print(f"{k}: {hardness_stat[k]}, {hardness_stat[k][0]/hardness_stat[k][1]}")
    print("cons")
    for k in method_stat:
        if method_stat[k][1] != 0:
            print(f"{k}: {method_stat[k]}, {method_stat[k][0]/method_stat[k][1]}")
    
    
    for rlt in results:
        testcase, score, method = rlt
        if "orig" in testcase:
            ood_stat["orig"][score[2]][1] += 1
            ood_stat["orig"]["all"][1] += 1
            if score[0] == 1:
                ood_stat["orig"][score[2]][0] += 1
                ood_stat["orig"]["all"][0] += 1
    
    print()
    a1 = 0
    for k in ood_stat:
        for m in ood_stat[k]:
            if ood_stat[k][m][1] != 0:
                print(f"{k}-{m}: {ood_stat[k][m]}, {ood_stat[k][m][0]/ood_stat[k][m][1]}")