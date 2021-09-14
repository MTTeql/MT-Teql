import random

def adaptive_sampling_first(train, split:float=0.9):
    original_train = [t for t in train if t["method"]=="seed"]
    sampled_train = random.sample(original_train, int(len(original_train)*split))
    sampled_train_testcase = set([t["testcase"].split("__")[0] for t in sampled_train])
    remaining_mutations = [t for t in train if t["testcase"].split("__")[0] not in sampled_train_testcase]
    return sampled_train, remaining_mutations

def adaptive_sampling_second(train, rate_dict):
    original_train = [t for t in train if t["method"]=="seed"]
    # num_orig = len(original_train)
    num_orig = 52215
    methods = []
    rate = []
    for k in rate_dict:
        methods.append(k)
        rate.append(rate_dict[k])
    # normalization
    factor = 1/sum(rate)
    rate = [r*factor for r in rate]

    sampled_train = []
    for i in range(len(methods)):
        samples = [t  for t in train if t["method"]==methods[i]]
        if len(samples) > int(rate[i]*num_orig):
            sampled_train_m = random.sample(samples, int(rate[i]*num_orig))
            sampled_train += sampled_train_m
        else:
            sampled_train += samples
    
    if len(sampled_train) < num_orig:
        sampled_id = [s["testcase"] for s in sampled_train]
        sampled_id = set(sampled_id)
        unsampled = [t for t in train if t["method"]!="seed" and t["testcase"] not in sampled_id]
        sampled_train += random.sample(unsampled, num_orig - len(sampled_train))

    sampled_train += original_train
    random.shuffle(sampled_train)
    return sampled_train