#!/usr/bin/env python2


import numpy as np
import python_module as pm
import dataset_io as dio

c = dio.loading_data('../data/10_weeks_doors.txt')

model = pm.python_function_update(c)

for i in xrange(10):
    print(pm.python_function_estimate(model, c[-1, 0] + i * 60))
