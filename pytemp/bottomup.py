import numpy as np
from functools import partial

class Leaf:
    '''leaf of a hierarchical tree'''
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'Leaf({self.value.tolist()})'


class Merged:
    '''branch of a hierarchical tree'''
    def __init__(self, children, order):
        self.children = children
        self.order = order

    def __repr__(self):
        return f'Merged(#={len(self.children)}, order={self.order})'


def get_values(cluster):
    if isinstance(cluster, Leaf):
        return [cluster.value]
    return [
        value for child in cluster.children for value in get_values(child)
    ]

def eudist(lvec, rvec):
    '''distance between data points'''
    return np.sqrt(((lvec - rvec)**2).sum())

def clust_dist(lclust, rclust, distagg=min):
    return distagg(
        eudist(lvec, rvec) 
        for lvec in get_values(lclust) for rvec in get_values(rclust)
    )

def pair_dist(pair, distagg=min):
    return clust_dist(pair[0], pair[1], distagg=distagg)

def get_order(cluster):
    if isinstance(cluster, Leaf):
        return np.inf
    return cluster.order

def get_children(cluster):
    if isinstance(cluster, Leaf):
        raise TypeError('Leaf has no children')
    return cluster.children
    
def bottom_up(data, distagg=min):
    clusters = [Leaf(vec) for vec in data]
    while len(clusters) > 1:
        c1, c2 = min(
            (   
                (cluster1, cluster2)
                for i, cluster1 in enumerate(clusters)
                for cluster2 in clusters[:i] 
            ), key=partial(pair_dist, distagg=distagg)
        )
        # remove c1 and c2
        clusters.remove(c1)
        clusters.remove(c2)
        merged = Merged([c1, c2], order=len(clusters))
        clusters.append(merged)
    # only one cluster left
    return clusters[0]

def gen_clusters(base_cluster, nClusters):
    clusters = [base_cluster]
    while len(clusters) < nClusters:
        nxt = min(clusters, key=get_order)
        clusters.remove(nxt)
        clusters.extend(get_children(nxt))
    return clusters


if __name__ == '__main__':

    import matplotlib.pyplot as plt

    with open('loci.csv') as fin:
        data = np.array([
            [int(num) for num in line.strip().split(',')]
            for line in fin
        ])
    # base cluster
    base = bottom_up(data, max)
    cs = [get_values(cl) for cl in gen_clusters(base, 3)]

    for i, clust, marker, colour in zip([1, 2, 3], cs, ['D', 'o', '*'], ['r', 'g', 'b']):
        xs, ys = zip(*clust)
        plt.scatter(xs, ys, color=colour, marker=marker)
        mx, my = np.mean(xs), np.mean(ys)
        plt.plot(mx, my, marker=f'${i}$', color='black')

    plt.title('User Locations -- 3 Bottom-Up Clusters, Min')
    plt.xlabel('blocks east of city centre')
    plt.ylabel('blocks north of city centre')
    plt.show()
