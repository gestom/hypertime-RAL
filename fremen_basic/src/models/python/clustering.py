import numpy as np
import scipy as sp
import basics as bs
import calibration as ca

def iteration(X, k, structure, params, max_iter=100):
    """
    """
    C, U = initialization(X, k, structure, params)
    C_prev = np.empty_like(C)
    WEIGHTS = np.empty_like(U)
    for i in xrange(max_iter):
        for cluster in xrange(k):
            weights = U[cluster]
            #C[cluster] = np.dot(weights, X) / np.sum(weights)
            C[cluster] = bs.averaging(X, weights, structure, params[0])
            XminusC = bs.substraction(X, C[cluster], params[0], structure)
            WEIGHTS[cluster] = weights_matrix(XminusC, weights, params[1])
        U = partition_matrix(WEIGHTS, params[1])
        if np.max(bs.distance(C_prev - C, did='E')) < 0.01:
            break
        else:
            np.copyto(C_prev, C)
    return C, U



def initialization(X, k, structure, params):
    """
    """
    n, d = np.shape(X)
    C = np.empty((k, d))
    WEIGHTS = np.empty((k, n))

    # initialize M to random, initialize C to spherical with variance 1
    for cluster in xrange(k):
        C[cluster] = X[np.random.choice(n)]
        XminusC = bs.substraction(X, C[cluster], 'def', structure)
        WEIGHTS[cluster] = weights_matrix(XminusC, weights=None, uid='hard')
    U = partition_matrix(WEIGHTS, uid='hard')
    return C, U
    


def partition_matrix(WEIGHTS, uid):
    """
    """
    if uid == 'fuzzy' or uid == 'normed':
        U = (WEIGHTS / np.sum(WEIGHTS, axis=0, keepdims=True)) ** 2
    elif uid == 'gmm':
        U = (WEIGHTS / np.sum(WEIGHTS, axis=0, keepdims=True))
    elif uid == 'hard':
        indices = np.argmax(WEIGHTS, axis=0)
        U = np.zeros_like(WEIGHTS)
        U[indices, np.arange(np.shape(WEIGHTS)[1])] = 1
    else:
        print('unknown type of partitioning, returning hard partitioning')
        U = partition_matrix(WEIGHTS, uid='hard')
    return U
        

def weights_matrix(XminusC, weights, uid):
    """
    """
    if uid == 'fuzzy' or uid == 'hard':
        # Euclidean distance
        D_square = np.sum((XminusC)**2, axis=1)
        W_part = 1 / (D_square + np.exp(-100))
    elif uid == 'GK':
        # Gustafson-Kessel distance
        SIGMA_star = np.cov(XminusC, bias=True, rowvar=False, aweights=weights)
        p = np.shape(SIGMA_star)[0]
        Det = np.linalg.det(SIGMA_star)
        if Det < 0:
            print('negative determinant')
            Det = np.abs(Det)
        if Det == 0:
            print('zero determinant')
            Det = 1e-15
        SIGMA = SIGMA_star / (Det ** (1 / p))
        try:
            SIGMA_inv = np.linalg.inv(SIGMA)
        except:
            print(sys.exc_info()[0])
            print('inversion not possible, using pseudoinversion')
            SIGMA_inv = np.linalg.pinv(SIGMA)
        D_square = np.sum(np.dot(XminusC, SIGMA_inv) * XminusC, axis=1)
        W_part = 1 / (D_square + np.exp(-100))
    elif uid == 'gmm':
        # weights from the multivariate normal distribution
        COV = np.cov(XminusC, bias=True, rowvar=False, aweights=weights)
        if len(np.shape(COV)) == 0:
            dim = 1
        else:
            dim = np.shape(COV)[0]
        # np.mean(weights) is p_i of the cluster
        W_part = np.mean(weights) * sp.stats.multivariate_normal.pdf(XminusC, np.zeros(dim), COV, allow_singular=True)
    elif uid == 'normed':
        # distances in a space with basis gathered by the normalization of the cluster shape
        COV = np.cov(XminusC, bias=True, rowvar=False, aweights=weights)
        #P = np.linalg.inv(sp.linalg.sqrtm(COV))
        P = ca.sqrt_inv(COV)
        D_square = np.sum(np.dot(XminusC, P) * XminusC, axis=1)
        W_part = 1 / (D_square + np.exp(-100))
    else:
        print('unknown type of weights, returning weights based on the Euclidean distance')
        W_part = weights_matrix(XminusC, weights, uid='dist')
    return W_part
































