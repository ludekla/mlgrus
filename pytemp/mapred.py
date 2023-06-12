from collections import Counter, defaultdict
from typing import List, Iterator, Tuple, Iterable, Callable, Any, NamedTuple
import datetime

def tokenise(doc: str) -> List[str]:
    '''just split on whitespace'''
    return doc.split()

def word_count_old(docs: List[str]):
    '''Word count not using MapReduce'''
    return Counter(word for doc in docs for word in tokenise(doc))

def wc_mapper(doc: str) -> Iterator[Tuple]:
    for word in tokenise(doc):
        yield word, 1

def wc_reducer(word: str, counts: Iterable[int]) -> Iterator[Tuple[str, int]]:
    yield word, sum(counts)


def word_count(docs: List[str]) -> List[Tuple[str, int]]:
    '''MapReduce implementation'''
    collector = defaultdict(list)
    for doc in docs:
        for word, count in wc_mapper(doc):
            collector[word].append(count)
    return [
        output for word, counts in collector.items() for output in wc_reducer(word, counts)
    ]

KV = Tuple[Any, Any] # key-value pair
Mapper = Callable[..., Iterable[KV]] # that's what a mapper is
#a reducer takes a key and an iterator, returns a key-value pair
Reducer = Callable[[Any, Iterable], Iterator[KV]]

def map_reduce(inputs: Iterable, mapper: Mapper, reducer: Reducer) -> List[KV]:
    '''Run MapReduce on the inputs using mapper and reducer'''
    collector = defaultdict(list)
    for inp in inputs:
        for key, value in mapper(inp):
            collector[key].append(value)
    return [
        output for key, values in collector.items() for output in reducer(key, values)   
    ]

def values_reducer(values_fn: Callable) -> Reducer:
    '''Return a reducer that applies values_fn to inputs'''
    def reducer(key: Any, values: Iterable) -> Iterator[KV]:
        yield key, values_fn(values)
    return reducer

def day_mapper(status: dict) -> Iterable:
    '''yields (day of week, 1) if status contains "data science"'''
    if "data science" in status["text"].lower():
        yield status["created_at"].weekday(), 1

def words_per_user_mapper(status: dict):
    user = status['username']
    for word in tokenise(status['text']):
        yield user, (word, 1)

def most_popular_word_reducer(user: str, words_and_counts: Iterable[KV]):
    '''
    Given the a sequence of (word, count) pairs, 
    return the word with the highest possible count
    '''
    wcounts = Counter()
    for word, count in words_and_counts:
        wcounts[word] += count
    word, count = wcounts.most_common(1)[0]
    yield user, (word, count)

def liker_mapper(status: dict):
    user = status['username']
    for liker in status['liked_by']:
        yield user, liker

def count_distinct_reducer(user: str, likers: Iterable[str]):
    yield user, len(likers)

class Entry(NamedTuple):
    name: str
    i: int
    j: int
    value: float

def matrix_multiply_mapper(nRows_a: int, nCols_b: int) -> Mapper:
    def mapper(entry: Entry):
        if entry.name == 'A':
            for y in range(nCols_b):
                key = (entry.i, y)
                value = (entry.j, entry.value)
                yield key, value
        else:
            for x in range(nRows_a):
                key = (x, entry.j)
                value = (entry.i, entry.value)
                yield key, value
    return mapper

def matrix_multiply_reducer(key: Tuple[int, int], indexed_values: Iterable[Tuple[int, int]]):
    results_by_index = defaultdict(list)
    for index, value in indexed_values:
        results_by_index[index].append(value)
    sumproduct = sum(
        values[0]*values[1] for values in results_by_index.values() 
        if len(values) == 2
    )
    if sumproduct != 0.0:
        yield key, sumproduct


if __name__ == '__main__':

    docs = ['data science', 'big data', 'science fiction']
    wc = word_count(docs)

    wc2 = map_reduce(docs, wc_mapper, wc_reducer)

    sumred = values_reducer(sum)
    maxred = values_reducer(max)
    minred = values_reducer(min)

    res = sumred('key', [1, 2, 3, 4, 5])

    status_updates = [
        {
            "id": 2,
            "username" : "joelgrus",
            "text" : "Should I write a second edition of my data science book? Should I not?",
            "created_at" : datetime.datetime(2018, 2, 21, 11, 47, 0),
            "liked_by" : ["data_guy", "data_gal", "mike"] 
        }, 
        {
            "id": 3,
            "username" : "lutzkla",
            "text" : "Should I write a second edition of my data science book? A second ?",
            "created_at" : datetime.datetime(2018, 2, 22, 11, 47, 0),
            "liked_by" : ["data_guy", "dirkygal", "dirkyman"] 
        },
        {
            "id": 1,
            "username" : "lutzkla2",
            "text" : "Should I write a second edition of my data book? My book?",
            "created_at" : datetime.datetime(2018, 3, 22, 11, 47, 0),
            "liked_by" : ["data_guy", "lutzkla2"] 
        },
    ]

    days = map_reduce(status_updates, day_mapper, sumred)
    words = map_reduce(status_updates, words_per_user_mapper, most_popular_word_reducer)
    likers = map_reduce(status_updates, liker_mapper, count_distinct_reducer)

    A = [[3, 2, 0], [0, 0, 0]]
    B = [[4, -1, 0], [10, 0, 0], [0, 0, 0]]

    entries = [
        Entry('A', 0, 0, 3), Entry('A', 0, 1, 2),
        Entry('B', 0, 0, 4), Entry('B', 0, 1, -1), Entry('B', 1, 0, 10)
    ]
    mapper = matrix_multiply_mapper(2, 3)
    mr = map_reduce(entries, mapper, matrix_multiply_reducer)