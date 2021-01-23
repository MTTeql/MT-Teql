import random
import json 


def stratified_sampling(mutations, size):
    assert size <= len(mutations)
    mutations = [m for m in mutations if m["method"]!="seed"]
    mutations_by_method = {}
    for m in mutations:
        if m["method"] in mutations_by_method:
            mutations_by_method[m["method"]].append(m)
        else:
            mutations_by_method[m["method"]] = [m]
    
    sampled_mut = []

    method_num = len(list(mutations_by_method.keys()))

    for method in mutations_by_method:
        if len(mutations_by_method[method]) < size // method_num:
            sampled_mut += mutations_by_method[method]
        else:
            sampled_mut += random.sample(mutations_by_method[method], size // method_num)
    
    if len(sampled_mut) < size:
        unpicked_mut = []
        picked_testcase = [i["testcase"] for i in sampled_mut]
        picked_testcase = set(picked_testcase)
        for m in mutations:
            if m["testcase"] not in picked_testcase:
                unpicked_mut.append(m)
        sampled_mut += random.sample(unpicked_mut, size-len(sampled_mut))
    
    return sampled_mut