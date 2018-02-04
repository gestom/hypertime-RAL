#!/usr/bin/env python2


import numpy as np
import python_module as pm
import dataset_io as dio

"""
c = dio.loading_data('../data/10_weeks_doors.txt')

model = pm.python_function_update(c)

for i in xrange(10):
    print(pm.python_function_estimate(model, c[-1, 0] + i * 60))
"""

C = np.arange(20).reshape((5, 4))
COV = np.arange(20).reshape((5, 2, 2))
DI = np.arange(5).reshape((5, 1))
structure = [0, [1.0, 1.0], [86400.0, 640000.0]]
k = 6


out_array = pm.python_function_model_to_array((C, COV, DI, structure, k))

out_model = pm.python_function_array_to_model(out_array)

print(C)
print(out_model[0])
print(COV)
print(out_model[1])
print(DI)
print(out_model[2])
print(structure)
print(out_model[3])
print(k)
print(out_model[4])
