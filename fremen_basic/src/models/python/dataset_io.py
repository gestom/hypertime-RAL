# Created on Fri Jun  2 13:52:33 2017
# @author: tom

"""
There are three used functions, the first loads data from file, the second
transforms these data to the requested space-hypertime and the third function
returns directory of this file.
Other functions were built only for testing.

loading_data(path):
loads data from file on adress 'path' of structure (t, x, y, ...),
    the first dimension (variable, column) is understood as a time,
    others are measured variables in corresponding time.
    If there is only one column in the dataset, it is understood as positive
    occurences in measured times. Expected separator between values is SPACE
    (' ').

create_X(data, structure): create X from a loaded data as a data in hypertime,
                           where the structure of a space is derived from
                           the varibale structure
where
input: data numpy array nxd*, matrix of measures IRL, where d* is number
       of measured variables
       structure list(int, list(floats), list(floats)),
                      number of non-hypertime dimensions, list of hypertime
                      radii nad list of wavelengths
and
output: X numpy array nxd, matrix of measures in hypertime
"""

import numpy as np


def create_X(data, structure, transformation):
    """
    input: data numpy array nxd*, matrix of measures IRL, where d* is number
                                  of measured variables
           structure list(int, list(floats), list(floats)),
                      number of non-hypertime dimensions, list of hypertime
                      radii nad list of wavelengths
    output: X numpy array nxd, matrix of measures in hypertime
    uses: np.empty(), np.c_[]
    objective: to create X as a data in hypertime, where the structure
               of a space is derived from the varibale structure
    """
    if transformation == 'circles':    
        # transformation: for every period one circe
        dim = structure[0]
        radii = structure[1]
        wavelengths = structure[2]
        X = np.empty((len(data), dim + len(radii) * 2))
        X[:, : dim] = data[:, 1: dim + 1]
        for period in range(len(radii)):
            r = radii[period]
            Lambda = wavelengths[period]
            X[:, dim: dim + 2] = np.c_[r * np.cos(data[:, 0] * 2 * np.pi / Lambda),
                                       r * np.sin(data[:, 0] * 2 * np.pi / Lambda)]
            dim = dim + 2
    elif transformation == 'circles_dicrete':    
        # transformation: for every period one circe
        dim = structure[0]
        radii = structure[1]
        wavelengths = structure[2]
        X = np.empty((len(data), dim + len(radii) * 2))
        X[:, : dim] = data[:, 1: dim + 1]
        for period in range(len(radii)):
            r = radii[period]
            Lambda = wavelengths[period]
            # POKUS !!!!
            if period > 0:
                X[:, dim: dim + 2] = np.c_[r * np.cos((np.floor(data[:, 0] / wavelengths[period - 1])) * 2 * np.pi / (wavelengths[period] / wavelengths[period - 1])),
                                           r * np.sin((np.floor(data[:, 0] / wavelengths[period - 1])) * 2 * np.pi / (wavelengths[period] / wavelengths[period - 1]))]    
                dim = dim + 2
            else:
                # KONEC POKUSU !!!
                X[:, dim: dim + 2] = np.c_[r * np.cos(data[:, 0] * 2 * np.pi / Lambda),
                                           r * np.sin(data[:, 0] * 2 * np.pi / Lambda)]
                dim = dim + 2
    elif transformation == 'torus':
        # transformation: multidimensional torus
        dim = structure[0]
        radii = structure[1]
        wavelengths = structure[2]
        # indexes sorted by length of waves
        # therefore the longest wawelength will have largest radius
        #sorted_indexes = np.argsort(wavelengths)
        sorted_indexes = np.argsort(np.array(wavelengths))
        #X = np.empty((len(data), dim + len(radii) + 1))
        X = np.zeros((len(data), dim + len(radii) + 1))
        X[:, : dim] = data[:, 1: dim + 1]
        X[:, -1] = radii[sorted_indexes[0]]
        for i in range(len(radii) - 1):
            # asi je to jedno, ale stavim to od nejmensiho polomeru, takze ty
            # promenne skladam do toho X odzadu
            r = radii[sorted_indexes[i + 1]]
            Lambda = wavelengths[sorted_indexes[i]]
            X[:, -i - 2] = X[:, -i - 1] * np.cos(data[:, 0] * 2 * np.pi / Lambda) + r
        if len(radii) == 1:
            X[:, -2] = X[:, -1]
        else:
            i += 1
            X[:, -i - 2] = X[:, -i - 1]
        for j in range(len(radii)):
            Lambda = wavelengths[sorted_indexes[j]]
            X[:, -j - 1] = X[:, -j - 1] * np.sin(data[:, 0] * 2 * np.pi / Lambda)
        j += 1
        X[:, -j - 1] = X[:, -j - 1]  * np.cos(data[:, 0] * 2 * np.pi / Lambda)
    else:
        print('bad transformation, returning untransformed data')
        X = data
    return X



def divide_dataset(dataset):
    """
    input: dataset numpy array, columns: time, vector of measurements, 0/1
                                  (occurence of event)
    output: training_data numpy array n*xd*, matrix of measures IRL, where
                                             d* is number of measured variables
                                             n* is 85% of measures
            evaluation_dataset numpy array, last 15% of dataset
            measured_time numpy array nX1, all measurement times
    uses: np.ceil(), np.split(),
    objective: to divide dataset to two parts (training and evaluation), 
               to create the "list" of all times of mesurements for fremen,
               to create training data of positive occurences of events
    """
    dividing_position = int(np.ceil(len(dataset) * 1))  # POKUS!!!
    training_dataset, evaluation_dataset =\
        np.split(dataset, [dividing_position])
    training_data = training_dataset[training_dataset[:, -1] == 1, 0: -1]
    # measured_times = training_dataset[:, 0]  # or [:, 0:1] ?
    ##### POKUS !!!
    return training_data, training_dataset, evaluation_dataset
    #return training_data, training_dataset
    ##### KONEC POKUSU !!!


def get_data(dataset):
    """
    """
    all_data = dataset[:, 0: -1]
    training_data = dataset[dataset[:, -1] == 1, 0: -1]
    return all_data, training_data


def hypertime_substraction(X, Ci, structure):
    """
    input: X numpy array nxd, matrix of n d-dimensional observations
           Ci_nxd numpy array nxd, matrix of n d-dimensional cluster centre
                                   copies
           structure list(int, list(floats), list(floats)),
                      number of non-hypertime dimensions, list of hypertime
                      radii nad list of wavelengths
    output: XC numpy array nxWTF, matrix of n WTF-dimensional substractions
    uses:
    objective: to substract C from X in hypertime
    """
    metrics = 'Euclidean'
    if metrics == 'Euclidean':
        # classical difference
        XC = X - Ci
    elif metrics == 'cosine':
        # cosine distance for hypertime and classical difference for space
        #non-hypertime dimensions substraction
        observations = np.shape(X)[0]
        ones = np.ones((observations, 1))
        dim = structure[0]
        radii = structure[1]
        XC = np.empty((observations, dim + len(radii)))
        XC[:, : dim] = X[:, : dim] - Ci[:, : dim]
        # hypertime dimensions substraction
        for period in range(len(radii)):
            r = radii[period]
            cos = (np.sum(X[:, dim + (period * 2): dim + (period * 2) + 2] *
                          Ci[:, dim + (period * 2): dim + (period * 2) + 2],
                          axis=1, keepdims=True) / (r ** 2))
            cos = np.minimum(np.maximum(cos, ones * -1), ones)
            XC[:, dim + period: dim + period + 1] = r * np.arccos(cos)
    else:
        print('unknown metrics, returning Euclidean metrics')
        XC = X - Ci
    return XC


