from sklearn import neighbors
import numpy as np

def get_data(filename):
    with open(filename) as fin:
        return np.array([
            [float(x) for x in line.strip().split(',')]
            for line in fin
        ])


if __name__ == '__main__':

    data = get_data('data/iris.csv')
    np.random.shuffle(data)
    Xtrain, Xtest = data[:100, -1:], data[100:, -1:]
    ytrain, ytest = data[:100, -1], data[100:, -1]

    knn = neighbors.KNeighborsClassifier(4)
    knn.fit(Xtrain, ytrain)

    for k in range(1, 101):
        knn.n_neighbors = k
        sc = knn.score(Xtest, ytest)
        print(f'k: {k} accuracy: {sc}')
