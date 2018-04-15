import numpy as np
from scipy.stats import multivariate_normal
import scipy as sp

import dataset_io as dio

import clustering as cl
import basics as bs
import calibration as ca
import estimation as es
import grid as gr
import learning as lrn

from time import clock



#################
# prerequisities
#################
dataset = np.loadtxt('../data/training_data.txt')
# for the model of "zeros"
#dataset[:, 1] = np.abs(dataset[:, 1] - 1)
# only training data
#data = dio.divide_dataset(dataset)[0]
#data = dataset[:, 0:1]

"""
# trivial parameters of the model
k = 5
structure = [0, [1.0, 1.0], [86400.0, 604800.0]]
#structure = [0, [2.0], [60*60*24.0]]
#structure = [0, [2.0], [60*60*24.0*7]]
transformation = 'circles'
max_iter=200

# transform measurements into circles
X = dio.create_X(data, structure, transformation)
"""

# params options
# sid: cos, def, cos-def
# uid: fuzzy, hard, gmm, normed
# did: gauss, uniform, trimmed_gauss, tailed_uniform
################ norm mi pripada dost na houby
################ hard mi pripada na houby
params = ('def', 'normed', 'tailed_uniform')

edges_of_cell = [60]
edges_of_big_cell = [3600]
transformation = 'circles'
max_number_of_periods = 16  # not used for eveluation[0] = False
wavelength_limits = [3600*24*7*2, 3600*6]  # longest, shortest not used for evaluation[0] = False
structure = [0, [1.0, 1.0, 1.0], [86400.0, 604800.0, 21600.0]]  # not used for evaluation[0] = True
k = 7  # not used for evaluation[0] = True
evaluation = [False, edges_of_cell, edges_of_big_cell, transformation, max_number_of_periods, wavelength_limits, structure, k]


all_data, training_data = dio.get_data(dataset)
domain_coordinates, domain_values = gr.get_domain(all_data, training_data, edges_of_cell, edges_of_big_cell)


C, densities, COV, k, params, structure = lrn.proposed_method(domain_coordinates, domain_values, training_data, params, evaluation)

import matplotlib.pyplot as plt
import matplotlib.colors as colors
plt.scatter(domain_coordinates[:10000], domain_values[:10000], color='b')
plt.scatter(all_data[:10000], domain_values[:10000], color='b')
plt.savefig("coordinates.png")
plt.close()

"""

#################
# clustering
#################

# gmm for potential comparison
#PI, MU, COV, U = gmm.gmm(X, k, structure, max_iter)
# clustering
#C, WEIGHTS, sid = cl.iteration(X, k, structure, max_iter)
#C, U = cl.iteration(X, k, structure, params, max_iter)


C, U = cl.iteration(X, k, structure, params, max_iter)




# where are the centers on the first circle?
import matplotlib.pyplot as plt
import matplotlib.colors as colors
plt.scatter(X[:, 0], X[:, 1], color='b')
plt.scatter(C[:,0], C[:,1], color='r')
plt.scatter(X[:, 2] * 1.3, X[:, 3] * 1.3, color='y')
plt.scatter(C[:,2] * 1.3, C[:,3] * 1.3, color='g')
#from mpl_toolkits.mplot3d import Axes3D
#ax = Axes3D(plt.figure())
#ax.scatter(X[:, 0], X[:, 1], X[:, 2], color='b')
#ax.scatter(C[:,0], C[:,1], C[:, 2], color='r')
plt.savefig("centres.png")
plt.close()


#################
# calibration
################

# input_coordinates should come from grid.py
edges_of_cell = [60]
edges_of_big_cell = [3600*2]
domain_coordinates = gr.get_domain(data, edges_of_cell, edges_of_big_cell)[0]
#domain_coordinates = gr.get_domain(dataset[:, 0:1], edges_of_cell, edges_of_big_cell)[0]
print(len(domain_coordinates))
DOMAIN = dio.create_X(domain_coordinates, structure, transformation)
densities, COV = ca.body(DOMAIN, X, C, U, k, params, structure)

"""


################
# estimation
###############
TESTING = dio.create_X(dataset[:, 0:1], structure, transformation)

out = es.training_model(TESTING, C, densities, COV, k, params, structure)






#plt.close()
X_test_values = dataset[:, 1]

print(np.sqrt(np.sum((out - X_test_values) ** 2)))
#training_dataset = dio.divide_dataset(dataset)[1]
#X_test_values = training_dataset[training_dataset[:, -1] == 1, :]
import matplotlib.pyplot as plt
#plt.plot(X_test[6000:9000], color='y')
#plt.plot(out[6000:9000], color='g')
#plt.plot(out_a[6000:9000], color='b')
#plt.plot(out_1[6000:9000], color='r')
plt.plot(X_test_values[:10000], color='y')
plt.plot(out[:10000], color='g')
#plt.plot(out_a[:10000], color='b')
#plt.plot(out_1[:10000], color='r')
plt.ylim(-0.5, 2)
plt.savefig("temp.png")
plt.close()



"""
#########################################################
# FIND WEIGHTS ON THE WHOLE TRAINING DATASET, aka "model"
# CALIBRATION
#########################################################

# v tuto chvili mam X, C, WEIGHTS, k
print(WEIGHTS)
U = cl.partition_matrix(WEIGHTS, 'hard')
COV = []
for cluster in xrange(k):
    weights = U[cluster]
    XminusC = bs.substraction(X, C[cluster], sid, structure)
    COV.append(np.cov(XminusC, bias=True, rowvar=False, aweights=weights))
COV = np.array(COV)
Pi = np.mean(U, axis=1)
# ted mam X, C, WEIGHTS, k, COV, U, Pi
# ale potrebuji jen C, COV, Pi

print('toto jse C')
print(C)
print('toto je COV')
print(COV)
print('toto je Pi')
print(Pi)

X_vse = dio.create_X(dataset[:, 0:1], structure, transformation)
DIST = []
for cluster in xrange(k):
    X_MU = bs.substraction(X_vse, C[cluster], sid, structure)
    #DIST.append(bs.transf_dist(X_MU, 'MVN', COV[cluster]))
    DIST.append(bs.transf_dist(X_MU, 'NORM_MODEL', COV[cluster]))
DIST = np.array(DIST)

# a ted prepocitam Pi
#Pi_new = Pi * np.sum(U, axis=1) / np.sum(DIST, axis=1)
Pi_new = np.sum(U, axis=1) / np.sum(DIST, axis=1)

# cimz ziskavam Pi_new, C, COV  ... a to je muj model

print('nove Pi')
print(Pi_new)    
#print('soucet DIST')
#print(np.sum(DIST))
#print(np.sum(DIST, axis=1))
#print(np.max(DIST, axis=1))
#out = (DIST).sum(axis=0)  
    


#######################
# WHOLE MODEL CREATED
# CALLING 'ESTIMATE'
#######################
print('a nyni jakoze estimate')
X_testovaci = dio.create_X(dataset[:, 0:1], structure, transformation)
#X_testovaci = X
DIST = []
for cluster in xrange(k):
    X_MU = bs.substraction(X_testovaci, C[cluster], sid, structure)
    #DIST.append(Pi_new[cluster] * bs.transf_dist(X_MU, 'MVN', COV[cluster]))
    DIST.append(Pi_new[cluster] * bs.transf_dist(X_MU, 'NORM_MODEL', COV[cluster]))
DIST = np.array(DIST)
#out = (DIST).sum(axis=0)  
out = (DIST).max(axis=0)  # for 'NORM_MODEL'

print('soucet DIST')
print(np.sum(DIST))
"""
