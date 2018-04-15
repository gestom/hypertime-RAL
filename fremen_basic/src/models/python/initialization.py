import numpy as np


def first_structure(training_data):
    """
    objective: to create initial structure
    todo: what anout different structure of structure, better for save and load to 'c++'
    """
    dim = np.shape(training_data)[1] - 1
    structure = [dim, [], []]
    return structure


def build_frequencies(longest, shortest):  # should be part of initialization of learning
    """
    input: longest float, legth of the longest wanted period in default
                          units
           shortest float, legth of the shortest wanted period
                           in default units
    output: W numpy array Lx1, sequence of frequencies
    uses: np.arange()
    objective: to find frequencies w_0 to w_k
    """
    k = int(longest / shortest) + 1
    W = np.float64(np.arange(k)) / float(longest)
    return W


