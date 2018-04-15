import numpy as np

import calibration as ca
import basics as bs


def training_model(DOMAIN, C, densities, COV, k, params, structure):
    """
    """
    #X_testovaci = dio.create_X(dataset[:, 0:1], structure, transformation)
    DIST = []
    for cluster in xrange(k):
        DOMAINminusC = bs.substraction(DOMAIN, C[cluster], params[0], structure)
        DIST.append(densities[cluster] * ca.distribution(DOMAINminusC, params[2], COV[cluster]))
    DIST = np.array(DIST)
    domain_values_estimation = (DIST).max(axis=0)  
    """
    if params[3] == 'uniform' or params[3] == 'tailed_uniform':
        out = (DIST).max(axis=0)  
    else:
        out = (DIST).sum(axis=0)  
    """
    return domain_values_estimation
