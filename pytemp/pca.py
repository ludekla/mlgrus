import numpy as np

def load(filename):
    with open(filename) as fin:
        lines = [line.strip() for line in fin]
        data = np.array([
            [float(el) for el in line.split(',')]
            for line in lines
        ])
        return data[:, :4], data[:, 4:]
        
def demean(X):
    '''X: ndarray'''
    return X - X.mean(0)

def direction(x):
    '''x: ndarray -> ndarray'''
    mag = np.sqrt((x*x).sum())
    return x / mag

def directional_var(data, x):
    d = direction(x)
    x = data.dot(d)
    return (x*x).sum()

def directional_var_grad(data, x):
    d = direction(x)
    return 2 * data.T.dot(data).dot(d)

def first_pc(data, nrounds=100, step_size=0.1):
    guess = np.random.randn(len(data[0]))
    guess = direction(guess)
    for _ in range(nrounds):
        grad = directional_var_grad(data, guess)
        guess -= step_size * grad
    return direction(guess)

def project(direc, vec):
    '''(direc: ndarray, vec: ndarray) -> <vec, direc> direc'''
    return direc.dot(vec) * direc

# project to complement
def project2comp(direc, vec):
    '''(direc: ndarray, vec: ndarray) -> vec - <vec, direc> direc'''
    return vec - project(direc, vec)

def projectem2comp(direc, data):
    '''projects all data onto orthogonal complement of direc'''
    return np.array([project2comp(direc, v) for v in data])

def pca(data, ncomps):
    components = []
    for _ in range(ncomps):
        pc = first_pc(data, 200, 0.1)
        components.append(pc)
        data = projectem2comp(pc, data)
    return np.array(components)

def transform_vec(vec, components):
    return components.dot(vec)

def transformem(data, components):
    return transform_vec(data.T, components).T


if __name__ == '__main__':

    X, y = load('iris.csv')

    # centre the data
    Xc = demean(X)

    pcs = pca(Xc, 3)
    for i, pc in enumerate(pcs, 1):
        print(f'pc {i}', pc)

    Xt = transformem(Xc, pcs)
    print(Xt[:10])

    tvec = transform_vec(Xc[0], pcs)
    print(Xc[0], '->', tvec)

    # from sklearn.decomposition import PCA

    # pm = PCA(n_components=3)
    # X2D = pm.fit_transform(Xc)
    # print(pm.components_)
