import numpy as np
import scipy as sc

import basics as bs
import clustering as cl

def body(DOMAIN, X, C, U, k, params, structure):
    """
    output: densities, COV
    input_coordinates could be calculated here - not sure
    """
    U = cl.partition_matrix(U, 'hard')
    COV = []
    for cluster in xrange(k):
        weights = U[cluster]
        XminusC = bs.substraction(X, C[cluster], params[0], structure)
        # for the purposes of processor time save during estimation, COV will be transformed to NORM, if not gauss
        if params[2] == 'gauss':
            COV.append(np.cov(XminusC, bias=True, rowvar=False, aweights=weights))
        else:
            COV.append(sqrt_inv(np.cov(XminusC, bias=True, rowvar=False, aweights=weights)))
    COV = np.array(COV)
    
    # ??? load input coordinates ?
    #X_vse = dio.create_X(dataset[:, 0:1], structure, transformation)
    DIST = []
    for cluster in xrange(k):
        DOMAINminusC = bs.substraction(DOMAIN, C[cluster], params[0], structure)
        DIST.append(distribution(DOMAINminusC, params[2], COV[cluster]))
    DIST = np.array(DIST)
    densities = np.sum(U, axis=1) / np.sum(DIST, axis=1)
    #U_DOM = cl.partition_matrix(DIST, 'hard')
    #densities = np.sum(U, axis=1) / np.sum(DIST * U_DOM, axis=1)
    return densities, COV


def distribution(XminusC, did, COV):
    """
    """
    shp = np.shape(XminusC)
    if len(shp) == 1:  # one dimensional array of XminusD
        d = len(XminusC)
    else:
        d = shp[1]
    if did == 'gauss':
        # multivariate normal 
        DISTR = sc.stats.multivariate_normal.pdf(XminusC, np.zeros(d), COV, allow_singular=True)
    elif did == 'uniform':
        sigma_multiplier = 2.0  # 1.732  # do kolika "sigma" se to povazuje za rovnomerne 
        DISTANCE = np.sqrt(np.sum(np.dot(XminusC, COV) * XminusC, axis=1))
        VICINITY = 1 / (DISTANCE + np.exp(-100))
        DISTR = np.empty_like(VICINITY)
        np.copyto(DISTR, VICINITY)
        DISTR[VICINITY > (1 / sigma_multiplier)] = (1 / sigma_multiplier)
        DISTR[VICINITY < (1 / sigma_multiplier)] = 0  # no tail
    elif did == 'tailed_uniform':
        sigma_multiplier = 2.0  # 1.732  # do kolika "sigma" se to povazuje za rovnomerne 
        DISTANCE = np.sqrt(np.sum(np.dot(XminusC, COV) * XminusC, axis=1))
        VICINITY = 1 / (DISTANCE + np.exp(-100))
        DISTR = np.empty_like(VICINITY)
        np.copyto(DISTR, VICINITY)
        #DISTR[VICINITY > (1 / sigma_multiplier)] = (1 / sigma_multiplier)
        DISTR[VICINITY > 1] = 1
        DISTR[VICINITY < (1 / sigma_multiplier)] **= 4  # tail
    elif did == 'trimmed_gauss':
        # multivariate normal 
        DIFFERENCE = np.dot(XminusC, COV)
        sigma_multiplier = 3.0  # 1.732  # do kolika "sigma" se to povazuje za rovnomerne 
        DISTANCE = np.sqrt(np.sum(np.dot(XminusC, COV) * XminusC, axis=1))
        DISTR = sc.stats.multivariate_normal.pdf(DIFFERENCE, np.zeros(d), np.eye(d), allow_singular=True)
        DISTR[DISTANCE > sigma_multiplier] = 0
    else:
        print('unknown distribution, returning uniform')
        DISTR = distribution(XminusC, 'uniform', COV)
    return DISTR

def sqrt_inv(COV):
    """
    """
    if len(np.shape(COV)) == 0:
        NORM = 1 / np.sqrt(COV)
    else:
        NORM = np.linalg.inv(sc.linalg.sqrtm(COV))
    return NORM
