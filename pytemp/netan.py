from typing import NamedTuple
from collections import deque
import numpy as np

from collections import Counter


class User(NamedTuple):
    ID: int
    name: str

def shortest_from(uid, friendships):
    # dict: user id -> all shortest paths to user  
    shpathTo = {uid: [[]]}
    # queue of (previous user, next user) needed to be checked
    frontier = deque((uid, fid) for fid in friendships[uid])
    # keep serving the queue
    while frontier:
        prevID, uID = frontier.popleft()
        paths2prev = shpathTo[prevID]
        newpaths = [path + [uID] for path in paths2prev]
        # in case we already know the shortest path
        oldpaths = shpathTo.get(uID, [])
        # shortest path to where we have been so far
        if oldpaths:
            minpathlen = len(oldpaths[0])
        else:
            minpathlen = float('inf')
        # keep paths that are new and not too long
        newpaths = [
            path for path in newpaths
            if len(path) <= minpathlen and path not in oldpaths 
        ]
        shpathTo[uID] = oldpaths + newpaths
        input(shpathTo)
        # add never-seen neighbours to the frontier
        frontier.extend((uID, fid) for fid in friendships[uID] if fid not in shpathTo)
        input(frontier)
    return shpathTo

def farness(uid, shortestPs):
    '''uid: user id Returns: sum of shortest paths to all users'''
    return sum(len(paths[0]) for paths in shortestPs[uid].values())

def adjamat(pairs, size):
    mat = np.zeros((size, size))
    for i, j in pairs:
        mat[i, j] = mat[j, i] = 1
    return mat

def page_rank(users, endorsements, damping=0.85, nIters=100):
    counts = Counter(target for _, target in endorsements)
    nUsers = len(users)
    pr = {user.ID: 1 / nUsers for user in users}
    base_pr = (1 - damping) / nUsers
    for _ in range(nIters):
        nxt_pr = {user.ID: base_pr for user in users}
        for source, target in endorsements:
            nxt_pr[target] += damping * pr[source] / counts[source]
        pr = nxt_pr
    return pr


if __name__ == '__main__':

    users = [
        User(0, "Hero"), User(1, "Dunn"), User(2, "Sue"), User(3, "Chi"),
        User(4, "Thor"), User(5, "Clive"), User(6, "Hicks"),
        User(7, "Devin"), User(8, "Kate"), User(9, "Klein")
    ]

    friend_pairs = [
        (0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4),
        (4, 5), (5, 6), (5, 7), (6, 8), (7, 8), (8, 9)
    ]

    friendships = {user.ID: [] for user in users}
    for i, j in friend_pairs:
        friendships[i].append(j)
        friendships[j].append(i)

    # sh = {user.ID: shortest_from(user.ID, friendships) for user in users}
    # # betweenness centrality
    # bcen = {user.ID: 0.0 for user in users}

    # for source in users:
    #     for targetID, paths in sh[source.ID].items():
    #         if source.ID >= targetID: # prevent double counting
    #             continue
    #         nPaths = len(paths)       # How many shortest paths?
    #         contrib  = 1 / nPaths     # contribution to centrality
    #         for path in paths:
    #             for betweenID in path:
    #                 if betweenID != source.ID and betweenID != targetID:
    #                     bcen[betweenID] += contrib

    # ccen = {user.ID: 1 / farness(user.ID, sh) for user in users}

    amat = adjamat(friend_pairs, len(users))


    endorsements = [
        (0, 1), (1, 0), (0, 2), (2, 0), (1, 2),
        (2, 1), (1, 3), (2, 3), (3, 4), (5, 4),
        (5, 6), (7, 5), (6, 8), (8, 7), (8, 9)
    ]

    pr = page_rank(users, endorsements)
    
