import random
import numpy as np
from collections import defaultdict

def squared_distance(lvec, rvec):
    return ((lvec - rvec)**2).sum()

def numdiff(lvec, rvec):
    '''counts the number of components that differ'''
    assert len(lvec) == len(rvec), 'input vectors need to have the same size'
    return sum(lv != rv for lv, rv in zip(lvec, rvec))

def cluster_means(k, inputs, assignments):
    clusters = dict.fromkeys(range(k))
    for inpt, assignment in zip(inputs, assignments):
        if clusters[assignment] is None:
            clusters[assignment] = [] 
        clusters[assignment].append(inpt)
    return {
        i: np.mean(cluster, axis=0) if cluster else random.choice(inputs)
        for i, cluster in clusters.items()
    }

class KMeans:
    '''k-means machine'''
    def __init__(self, k):
        self.k = k
        self.means = None

    def classify(self, inpt):
        return min(
            range(self.k), 
            key=lambda i: squared_distance(inpt, self.means[i])
        )

    def train(self, inputs):
        m = len(inputs)
        assignments = [np.random.randint(self.k) for _ in inputs]
        i = 0
        while True:
            i += 1
            print('round', i)
            # maximisation step
            self.means = cluster_means(self.k, inputs, assignments)
            # expectation step
            new_assignments = [self.classify(inpt) for inpt in inputs]
            nchanged = numdiff(assignments, new_assignments)
            if nchanged == 0:
                break
            assignments = new_assignments
        return sum(squared_distance(v, self.means[i]) for v, i in zip(inputs, assignments))


def error(inputs, k):
    km = KMeans(k)
    return km.train(inputs)

def recolour(km, vec):
    '''pixel vector of dim 3'''
    clusterID = km.classify(vec)
    return [int(val) for val in km.means[clusterID]]


if __name__ == '__main__':

    with open('loci.csv') as fin:
        data = np.array([
            [int(num) for num in line.strip().split(',')]
            for line in fin
        ])

    n = len(data)
    ks = list(range(1, n+1))
    errors = [error(data, k) for k in ks]

    print(errors)
    import matplotlib.pyplot as plt

    # plt.plot(ks, errors)
    # plt.xticks(ks)
    # plt.xlabel('k')
    # plt.ylabel('squared error')
    # plt.title('k-means')
    # plt.show()

    import matplotlib.image as mpimg
    # from PIL import Image

    img = mpimg.imread('lutz.jpg') # ndarray of shape ~ (1500, 3200, 3)
    # row = img[0]   # top row: ndarray of shape ~ (3200, 3)
    rows = np.array([pixel.tolist() for row in img for pixel in row])

    km = KMeans(5)   # goal: use 5 colours
    km.train(rows)

    new_img = np.array([
        [recolour(km, pixel) for pixel in row] for row in img
    ], dtype=np.uint8)

    # plt.imshow(new_img)
    plt.imsave('lutz5.jpg', new_img)
    # plt.show()