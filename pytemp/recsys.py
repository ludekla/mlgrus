import re
import numpy as np
import csv
from collections import Counter, defaultdict, namedtuple


users_interests = [
    ["Hadoop", "Big Data", "HBase", "Java", "Spark", "Storm", "Cassandra"],
    ["NoSQL", "MongoDB", "Cassandra", "HBase", "Postgres"],
    ["Python", "scikit-learn", "scipy", "numpy", "statsmodels", "pandas"],
    ["R", "Python", "statistics", "regression", "probability"],
    ["machine learning", "regression", "decision trees", "libsvm"],
    ["Python", "R", "Java", "C++", "Haskell", "programming languages"],
    ["statistics", "probability", "mathematics", "theory"],
    ["machine learning", "scikit-learn", "Mahout", "neural networks"],
    ["neural networks", "deep learning", "Big Data", "artificial intelligence"],
    ["Hadoop", "Java", "MapReduce", "Big Data"],
    ["statistics", "R", "statsmodels"],
    ["C++", "deep learning", "artificial intelligence", "probability"],
    ["pandas", "R", "Python"],
    ["databases", "HBase", "Postgres", "MySQL", "MongoDB"],
    ["libsvm", "regression", "support vector machines"]
]

MOVIES = 'movielens/ml-100k/u.item'
RATINGS = 'movielens/ml-100k/u.data'

Rating = namedtuple('Rating', 'userID movieID rating')

def get_movies():
    with open(MOVIES, encoding='iso-8859-1') as f:
        reader = csv.reader(f, delimiter='|')
        return {movieID: title for movieID, title, *_ in reader}

def get_ratings():
    with open(RATINGS, encoding='iso-8859-1') as f:
        reader = csv.reader(f, delimiter='\t')
        return [Rating(uID, mID, float(rating)) for uID, mID, rating, _ in reader]


def mostpop_new(uinterest, popular_ints, maxres=5):
    suggestions = [
        (interest, freq) for interest, freq in popular_ints.most_common()
        if interest not in uinterest  
    ]
    return suggestions[:maxres]


class InterestEncoder:
    '''Vectorises users interest'''
    def __init__(self, interests):
        self.interests = interests

    def __repr__(self):
        clsname = self.__class__.__name__
        return f'{clsname}(nInterests=len(self.interests))'

    def toBoolVec(self, interests):
        return [
            1 if interest in interests else 0 for interest in self.interests
        ]

def cossim(vecA, vecB):
    nA, nB = np.sqrt((vecA*vecA).sum()), np.sqrt((vecB*vecB).sum())
    return vecA.dot(vecB) / (nA * nB)

def mostSimUTo(usersims, userID):
    pairs = [
        (otherID, sim) for otherID, sim in enumerate(usersims[userID])
        if userID != otherID and sim > 0.0    
    ]
    return sorted(pairs, key=lambda p: p[1], reverse=True)

def mostSimITo(interests, interestSims, interestID):
    pairs = [
        (interests[otherID], sim) for otherID, sim in enumerate(interestSims[interestID])
        if interestID != otherID and sim > 0.0
    ]
    return sorted(pairs, key=lambda p: p[1], reverse=True)

def user_based_suggs(userID, user_sims, currentInts=False):
    suggs = defaultdict(float)
    for otherID, sim in mostsimUTo(user_sims, userID):
        for interest in users_interests[otherID]:
            suggs[interest] += sim
    if currentInts:
        return suggs
    suggestions = [
        (interest, sim) for interest, sim in suggs.items() 
        if interest not in users_interests[userID]
    ]
    suggestions.sort(key=lambda p: p[1], reverse=True)
    return suggestions

def interest_based_suggs(userID, uivecs, interests, interestSims, currentInts=False):
    suggs = defaultdict(float)
    for interestID, interested in enumerate(uivecs[userID]):
        if interested == 0:
            continue
        for interest, sim in mostSimITo(interests, interestSims, interestID):
            suggs[interest] += sim
    suggs = sorted(suggs.items(), key=lambda p: p[1], reverse=True)
    if currentInts:
        return suggs
    suggestions = [
        (interest, sim) for interest, sim in suggs
        if interest not in users_interests[userID]
    ]
    return suggestions

def loop(dataset, uembeds, membeds, lrate=None):
    loss = 0.0
    for rating in dataset:
        mvec = membeds[rating.movieID]
        uvec = uembeds[rating.userID]
        predicted = mvec.dot(uvec)
        error = predicted - rating.rating
        loss += error**2
        if lrate is not None:
            ugrad = error * mvec
            mgrad = error * uvec
            # update embeddings
            uvec -= lrate * ugrad
            mvec -= lrate * mgrad
    return loss


if __name__ == '__main__':

    # popints = Counter(interest for uinterest in users_interests for interest in uinterest)

    # suggs = mostpop_new(users_interests[0], popints)

    # interests = sorted(popints)
    # encoder = InterestEncoder(interests)
    # # user-interest matrix: every user is represented a row of interests
    # uimat = np.array([encoder.toBoolVec(interests) for interests in users_interests])
    # # user similarities: every row with every row
    # userSims = [[cossim(v, w) for v in uimat] for w in uimat]
    # print('Most similar users to user 0:')
    # m = mostSimUTo(userSims, 0)
    # print(m)

    # # suggs = user_based_suggs(0, usersims)

    # # interest-user matrix: every user is represented a column of interests
    # iumat = uimat.T
    # # interest similarities: every row with every row
    # interestSims = [[cossim(v, w) for v in iumat] for w in iumat]
    # print(f'Most similar interests to {interests[0]}:')
    # m = mostSimITo(interests, interestSims, 0)
    # print(m)

    # ibs = interest_based_suggs(0, uimat, interests, interestSims)
    # print(ibs)

    # 1682 movies rated by 943 users
    movies = get_movies()
    ratings = get_ratings()

    # star wars ratings
    RX = re.compile(r'Star Wars|Empire Strikes|Jedi')
    swr = {mID: [] for mID, title in movies.items() if RX.search(title)}

    for rating in ratings:
        if rating.movieID in swr:
            swr[rating.movieID].append(float(rating.rating))

    avg = [(sum(rats)/len(rats), mID) for mID, rats in swr.items()]
    for avg_rat, mID in avg:
        print(f'{avg_rat:0.2f}', movies[mID])

    split1 = int(len(ratings) * 0.7)
    split2 = int(len(ratings) * 0.85)

    train = ratings[:split1]
    validation = ratings[split1:split2]
    test = ratings[split2:]

    avg_rat = sum(rating.rating for rating in train) / len(train)
    baseline_error = sum((rating.rating - avg_rat)**2 for rating in test) / len(test) 

    EMBEDDING_DIM = 2
    # user ids and movie ids
    uids = {rating.userID for rating in ratings}
    mids = {rating.movieID for rating in ratings}
    # start with random embeddings for users and movies
    uvecs = {uid: np.random.randn(EMBEDDING_DIM) for uid in uids}
    mvecs = {mid: np.random.randn(EMBEDDING_DIM) for mid in mids}

    lrate = 0.05
    for epoch in range(20):
        lrate *= 0.9
        loss = loop(train, uvecs, mvecs, lrate)
        vloss = loop(validation, uvecs, mvecs)
        print(
            f'epoch: {epoch:2} learning rate: {lrate:0.4f} ' 
            f'loss: {loss:0.3f} validation: {vloss:0.3f}'
        )
    tloss = loop(test, uvecs, mvecs)
    print(f'test loss: {tloss:0.3f}')

    import pca

    ovecs = np.array([v for v in mvecs.values()])
    comps = pca.pca(ovecs, 2)

    ratingsByMovie = defaultdict(list)
    for rating in ratings:
        ratingsByMovie[rating.movieID].append(rating.rating)
    
    vectors = [
        (mID, sum(ratingsByMovie[mID])/len(ratingsByMovie[mID]), movies[mID], vec)
        for mID, vec in zip(mvecs.keys(), pca.transformem(ovecs, comps))
    ]

    svecs = sorted(vectors, key=lambda v: abs(v[3][0]))




