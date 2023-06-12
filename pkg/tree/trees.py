import json
import csv
import dataclasses
import numpy as np
from functools import partial
from collections import Counter, defaultdict, namedtuple
from dataclasses import dataclass


@dataclass
class Candidate:
    level:  str
    lang:   str
    tweets: bool
    phd:    bool
    didwell: bool


# cands =  [
#     Candidate('Senior', 'Java',   False, False, False),
#     Candidate('Senior', 'Java',   False, True,  False),
#     Candidate('Mid',    'Python', False, False, True),
#     Candidate('Junior', 'Python', False, False, True),
#     Candidate('Junior', 'R',      True,  False, True),
#     Candidate('Junior', 'R',      True,  True,  False),
#     Candidate('Mid',    'R',      True,  True,  True),
#     Candidate('Senior', 'Python', False, False, False),
#     Candidate('Senior', 'R',      True,  False, True),
#     Candidate('Junior', 'Python', True,  False, True),
#     Candidate('Senior', 'Python', True,  True,  True),
#     Candidate('Mid',    'Python', False, True,  True),
#     Candidate('Mid',    'Java',   True,  False, True),
#     Candidate('Junior', 'Python', False, True,  False)
# ]

# def save(jsnfile):
#     with open(jsnfile, mode='w') as jout:
#         data = [dataclasses.asdict(c) for c in cands]
#         json.dump(data, jout, indent=4)

def fromJSON(jsnfile):
    with open(jsnfile) as jout:
        cands = json.load(jout)
        return [Candidate(**dic) for dic in cands]

def fromCSV(csvfile):
    cands = []
    with open(csvfile) as fin:
        _ = next(fin)
        for line in fin:
            rec = line.strip().split(',')
            cand = Candidate(*rec)
            cand.tweets = bool(int(cand.tweets))
            cand.phd = bool(int(cand.phd))
            cand.didwell = bool(int(cand.didwell))
            cands.append(cand)
    return cands

def fromCSV2(csvfile):
    cands = []
    with open(csvfile) as fin:
        rd = csv.reader(fin)
        _ = next(fin)
        for rec in rd:
            cand = Candidate(*rec)
            cand.tweets = bool(int(cand.tweets))
            cand.phd = bool(int(cand.phd))
            cand.didwell = bool(int(cand.didwell))
            cands.append(cand)
    return cands

def entropy(probs):
    '''stats: List[float]'''
    probs = np.array([p for p in probs if p > 0])
    return -(probs*np.log2(probs)).sum()

def clsprobs(data):
    '''data: List[float]'''
    total = len(data)
    return [c/total for c in Counter(data).values()]

def data_entropy(data):
    '''data: List[float]'''
    return entropy(clsprobs(data))

def partition_entropy(partition):
    '''partition: List[List[float]]'''
    total = sum(len(subset) for subset in partition)
    return sum([len(subset)*data_entropy(subset)/total for subset in partition])

def partition_by(cands, attr):
    '''cands: List[Candidate] attr: str'''
    partition = defaultdict(list)
    for cand in cands:
        value = getattr(cand, attr)
        partition[value].append(cand)
    return partition

def partition_entropy_by(partition, attr):
    label_partition = [
        [getattr(c, attr) for c in cands] 
        for cands in partition.values()
    ]
    return partition_entropy(label_partition)

Leaf = namedtuple('Leaf', 'value')
Split = namedtuple('Split', 'attr subtree value')

def classify(tree, cand):
    # check whether the answer can be given
    # base case of the recursion: tree is just a leaf
    if isinstance(tree, Leaf):
        return tree.value
    # get the value of the split attribute to figure out the next subtree
    branch = getattr(cand, tree.attr)
    # return default value if value of attribute is unknown to the tree
    if branch not in tree.subtree:
        return tree.value
    # delegate the classification task to the subtree
    subtree = tree.subtree[branch]
    return classify(subtree, cand)

def build_tree(cands, split_attrs, target_attr):
    '''ID3 algorithm'''
    # count target labels
    labels = Counter(getattr(cand, target_attr) for cand in cands)
    most_common = labels.most_common(1)[0][0]
    # if unique label or if there are no split attributes
    # then return majority label
    if len(labels) == 1 or not split_attrs:
        return Leaf(most_common)
    # otherwise split by the best attribute
    impurity = partial(split_entropy, cands, target_attr)
    best_attr = min(split_attrs, key=impurity)
    partition = partition_by(cands, best_attr)
    new_attrs = [a for a in split_attrs if a != best_attr]
    subtrees = {
        attr_value: build_tree(subset, new_attrs, target_attr)
        for attr_value, subset in partition.items()
    }
    return Split(best_attr, subtrees, most_common)

def split_entropy(cands, target_attr, attr):
    partition = partition_by(cands, attr)
    return partition_entropy_by(partition, target_attr)

# def classem(cands, tree):
#     c = 0
#     for cand in cands:
#         didwell = classify(tree, cand)
#         print(f'{cand.didwell} was classified as {didwell}')
#         if didwell == cand.didwell:
#             c += 1
#     n = len(cands)
#     r = c/n
#     print(f'Result: {c} correct of {n} (ratio: {r})')


if __name__ == '__main__':

    # save('cands.json')

    # cands = fromJSON('cands.json')
    cands = fromCSV2('cands.csv')
    
    cs = [c.phd for c in cands]
    x = data_entropy(cs)
    print(x)

    p = partition_by(cands, 'phd')
    q = partition_by(cands, 'lang')

    print('phd partition by phd', partition_entropy_by(p, 'phd'))
    print('phd partition by lang', partition_entropy_by(p, 'lang'))
    print('lang partition by phd', partition_entropy_by(q, 'phd'))
    print('lang partition by lang', partition_entropy_by(q, 'lang'))

    htree0 = Split(
        'level', {
            'Junior': Split('phd', {False: Leaf(True), True: Leaf(False)}, None),
            'Mid': Leaf(True),
            'Senior': Split('tweets', {False: Leaf(False), True: Leaf(True)}, None)
        },
        False
    )
    for cand in cands:
        print(f'Hire? : {cand.didwell} - {classify(htree0, cand)}')

    print("learned tree")
    # classem(cands, htree0)    

    htree = build_tree(cands, ['level', 'phd', 'tweets', 'lang'], 'didwell')
    for cand in cands:
        print(f'Hire? : {cand.didwell} - {classify(htree, cand)}')


    # classem(cands, htree)

    cand = Candidate('Intern', 'Java', True, True, None)
    ans = classify(htree, cand)
    print(f'Hire?: trained tree says {ans}')
    ans = classify(htree0, cand)
    print(f'Hire?: handcrafted tree says {ans}')
    
        
