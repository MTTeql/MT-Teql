import json, random


def random_sampling(mutations, size):
    assert size <= len(mutations)
    mutations = [m for m in mutations if m["method"]!="seed"]
    sampled_mut = random.sample(mutations, size)
    
    return sampled_mut