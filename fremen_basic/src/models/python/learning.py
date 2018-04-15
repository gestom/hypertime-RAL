
# Created on Sun Aug 27 14:40:40 2017
# @author: tom

"""
returns parameters of the learned model
call proposed_method(longest, shortest, path, edge_of_square, timestep, k,
                     radius, number_of_periods, evaluation)
where
input: longest float, legth of the longest wanted period in default
                      units
       shortest float, legth of the shortest wanted period
                       in default units
       path string, path to file
       edge_of_square float, spatial edge of cell in default units (meters)
       timestep float, time edge of cell in default units (seconds)
       k positive integer, number of clusters
       radius float, size of radius of the first found hypertime circle
       number_of_periods int, max number of added hypertime circles
       evaluation boolean, stop learning when the error starts to grow?
and
output: C numpy array kxd, matrix of k d-dimensional cluster centres
        COV numpy array kxdxd, matrix of covariance matrices
        density_integrals numpy array kx1, matrix of ratios between
                                           measurements and grid cells
                                           belonging to the clusters
        structure list(int, list(floats), list(floats)),
                  number of non-hypertime dimensions, list of hypertime
                  radii nad list of wavelengths
        average DODELAT
"""

import numpy as np
from time import clock
import copy as cp

import fremen as fm
import initialization as it
import grid as gr
import dataset_io as dio
import clustering as cl
import calibration as ca
import basics as bs
import estimation as es


def proposed_method(domain_coordinates, domain_values, training_data, params, evaluation):
    """
    input: longest float, legth of the longest wanted period in default
                          units
           shortest float, legth of the shortest wanted period
                           in default units
           dataset numpy array, columns: time, vector of measurements, 0/1
                                (occurence of event)
           edge_of_square float, spatial edge of cell in default units (meters)
           timestep float, time edge of cell in default units (seconds)
           k positive integer, number of clusters
           radius float, size of radius of the first found hypertime circle
           number_of_periods int, max number of added hypertime circles
           evaluation boolean, stop learning when the error starts to grow?
    output: C numpy array kxd, matrix of k d-dimensional cluster centres
            COV numpy array kxdxd, matrix of covariance matrices
            density_integrals numpy array kx1, matrix of ratios between
                                               measurements and grid cells
                                               belonging to the clusters
            structure list(int, list(floats), list(floats)),
                      number of non-hypertime dimensions, list of hypertime
                      radii nad list of wavelengths
            average DODELAT
    uses: time.clock()
          init.whole_initialization(), iteration_step()
    objective: to learn model parameters
    """
    if evaluation[0] == False:
        # for the future to know the strusture of evaluation
        edges_of_cell = evaluation[1]
        edges_of_big_cell = evaluation[2]
        transformation = evaluation[3]
        max_number_of_periods = evaluation[4]  # not used here
        longest, shortest = evaluation[5]  # not used here
        structure = evaluation[6]  # not used for evaluation[0] = True
        k = evaluation[7]  # not used for evaluation[0] = True

        X = dio.create_X(training_data, structure, transformation)
        C, U = cl.iteration(X, k, structure, params)
        #domain_coordinates = gr.get_domain(data, edges_of_cell, edges_of_big_cell)[0]
        DOMAIN = dio.create_X(domain_coordinates, structure, transformation)
        densities, COV = ca.body(DOMAIN, X, C, U, k, params, structure)
    else:
        edges_of_cell = evaluation[1]
        edges_of_big_cell = evaluation[2]
        transformation = evaluation[3]
        max_number_of_periods = evaluation[4]
        longest, shortest = evaluation[5]
        # initialization
        frequencies = it.build_frequencies(longest, shortest)
        structure = it.first_structure(training_data)
        #domain_coordinates, domain_values = gr.get_domain(training_data, edges_of_cell, edges_of_big_cell)
        if structure[0] == 0 and structure[1] == []:
            # there is nothing to cluster, we have to create new structure with one 'circle' before clustering
            average = domain_values / len(domain_values)
            #C = np.array([average])
            #COV = C/10
            #densities = np.array([[average]])
            #k = 1
            #chosen_period(T, S, W)
            the_period = fm.chosen_period(domain_coordinates[:, 0], domain_values - average, frequencies)[0]
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            structure[1].append(bs.radius(the_period, structure))
            structure[2].append(the_period)
            WW = list(frequencies)
            WW.remove(1 / the_period)  # P
            frequencies = np.array(WW)
            print('periodicity ' + str(the_period) + ' chosen and the corresponding frequency removed')
        # create model
        #X = dio.create_X(training_data, structure, transformation)
        #DOMAIN = dio.create_X(domain_coordinates, structure, transformation)
        diff, C, densities, COV, the_period, k = best_k(training_data, domain_coordinates, domain_values, frequencies, 2, structure, params, transformation)
        jump_out = 0
        iteration = 0
        #diff = -1
        while jump_out == 0:
            print('\nstarting learning iteration: ' + str(iteration))
            print('with number of clusters: ' + str(k))
            print('and the structure: ' + str(structure))
            iteration += 1
            start = clock()
            jump_out, diff, C, densities, COV, the_period, structure, frequencies, k = \
                step_evaluation(diff, C, densities, COV, the_period, structure, frequencies, training_data, domain_coordinates, domain_values, transformation, k, params)
            finish = clock()
            print('structure: ' + str(structure) + ' and number of clusters: ' + str(k))
            print('leaving learning iteration: ' + str(iteration))
            print('processor time: ' + str(finish - start))
            if len(structure[1]) >= max_number_of_periods:
                jump_out = 1
            """
            else:
                # new: structure, DOMAIN, X, frequencies (and also k and the_period)
                structure[1].append(bs.radius(the_period, structure))
                structure[2].append(the_period)
                WW = list(frequencies)
                WW.remove(1 / the_period)  # P
                frequencies = np.array(WW)
                print('periodicity ' + str(P) + ' chosen and the corresponding frequency removed')
                X = dio.create_X(data, structure, transformation)
                DOMAIN = dio.create_X(domain_coordinates, structure, transformation)
            """
        print('learning iterations finished')
        """
        print('and the difference between model and reality at the end is:')
        if structure[0] == 0 and len(structure[1]) == 0:
            print('unknown, return average: ' + str(C[0]))
        else:
            if evaluation:
                list_of_diffs = []                                                       
                list_of_others = []                                                     
                for j in xrange(6):  # looking for the best clusters      
                    sum_of_amplitudes_j, Cj, Uj, COVj, density_integrals_j, Wj, ESj,\
                        Pj, diff_j = iteration_step(training_data, input_coordinates,   
                                         structure, C, U, k, shape_of_grid,       
                                         time_frame_sums, T, W, ES, valid_timesteps,    
                                         evaluation_dataset, edges_of_cell)             
                    list_of_diffs.append(diff_j)                            
                    list_of_others.append((Cj, COVj, density_integrals_j))                           
                best_position = np.argmin(list_of_diffs)
                diff = list_of_diffs[best_position]
                C, COV, density_integrals = list_of_others[best_position]
                print('all diffs in comparison: ' + str(list_of_diffs))
            else:
                diff = ev.evaluation_step(evaluation_dataset, C, COV, density_integrals,\
                                          structure, k, edges_of_cell)
        print(diff)
        print('using k = ' + str(k))
        print('and structure: ' + str(structure) + '\n\n')
        average = overall_sum / len(input_coordinates)
        return C, COV, density_integrals, structure, average, k
        """
    return C, densities, COV, k, params, structure  # to poradi pak budu muset zvazit


def step_evaluation(diff, C, densities, COV, the_period, structure, frequencies, training_data, domain_coordinates, domain_values, transformation, k, params):
    """
    input: path string, path to file
           input_coordinates numpy array, coordinates for model creation
           structure list(int, list(floats), list(floats)),
                      number of non-hypertime dimensions, list of hypertime
                      radii nad list of wavelengths
           C numpy array kxd, centres from last iteration
           U numpy array kxn, matrix of weights from the last iteration
           k positive integer, number of clusters
           shape_of_grid numpy array dx1 int64, number of cells in every
                                                dimension
           time_frame_sums numpy array shape_of_grid[0]x1, sum of measures
                                                            over every
                                                            timeframe
           T numpy array shape_of_grid[0]x1, time positions of timeframes
           W numpy array Lx1, sequence of reasonable frequencies
           ES float64, squared sum of squares of residues from this iteration
           COV numpy array kxdxd, matrix of covariance matrices
           density_integrals numpy array kx1, matrix of ratios between
                                              measurements and grid cells
                                              belonging to the clusters
           P float64, length of the most influential frequency in default
                      units
           radius float, size of radius of the first found hypertime circle
    output: jump_out int, zero or one - to jump or not to jump out of learning
            structure list(int, list(floats), list(floats)),
                      number of non-hypertime dimensions, list of hypertime
                      radii nad list of wavelengths
            C numpy array kxd, matrix of k d-dimensional cluster centres
            U numpy array kxn, matrix of weights
            COV numpy array kxdxd, matrix of covariance matrices
            density_integrals numpy array kx1, matrix of ratios between
                                               measurements and grid cells
                                               belonging to the clusters
            W numpy array Lx1, sequence of reasonable frequencies
            ES float64, squared sum of squares of residues from this iteration
            P float64, length of the most influential frequency in default
                       units
    uses: iteration_step()
          cp.deepcopy()
    objective: to send new or previous version of model (and finishing pattern)
    """
    new_structure = cp.deepcopy(structure)
    # new: structure, DOMAIN, X, frequencies (and also k and the_period)
    new_structure[1].append(bs.radius(the_period, new_structure))
    new_structure[2].append(the_period)
    WW = list(frequencies)
    WW.remove(1 / the_period)  # P
    new_frequencies = np.array(WW)
    print('periodicity ' + str(the_period) + ' chosen and the corresponding frequency removed')
    ##########################################
    last_best = best_k(training_data, domain_coordinates, domain_values, new_frequencies, k, new_structure, params, transformation)
    ##########################################
    if last_best[0] < diff or diff == -1:  # (==) if diff < diff_old
        diff, C, densities, COV, the_period, k = last_best
        structure = cp.deepcopy(new_structure)
        frequencies = np.empty_like(new_frequencies)
        np.copyto(frequencies, new_frequencies)
        jump_out = 0
    else:
        jump_out = 1
        print('\ntoo many periodicities, error of model have risen,')
        print('when structure ' + str(new_structure) + ' tested;')
        print('jumping out (prematurely)\n')
    return jump_out, diff, C, densities, COV, the_period, structure, frequencies, k


def best_k(training_data, domain_coordinates, domain_values, frequencies, k, new_structure, params, transformation):
    """
    """
    X = dio.create_X(training_data, new_structure, transformation)
    DOMAIN = dio.create_X(domain_coordinates, new_structure, transformation)
    last_best = ()
    sum_of_amplitudes = -1
    k_j = k
    all_params = []
    while True:
        #k = k + 1
        list_of_sums = []
        list_of_others = []
        list_of_diffs = []
        for j in xrange(5):  # for the case that the clustering would fail
            diff_j, C_j, densities_j, COV_j, the_period_j, sum_of_amplitudes_j =\
                iteration_step(DOMAIN, domain_values, domain_coordinates[:, 0], frequencies, X, k_j, new_structure, params)
            list_of_sums.append(sum_of_amplitudes_j)
            list_of_diffs.append(diff_j)
            list_of_others.append((diff_j, C_j, densities_j, COV_j, the_period_j, k_j))
        all_params.append(list_of_others)
        #chosen_model = np.argmin(list_of_sums)
        chosen_model = np.argmin(list_of_diffs)
        tested_sum_of_amplitudes = list_of_sums[chosen_model]
        if sum_of_amplitudes == -1:
            sum_of_amplitudes = tested_sum_of_amplitudes
            last_best = list_of_others[chosen_model]
            k_j = k_j + 1
        else:
            if tested_sum_of_amplitudes <= sum_of_amplitudes:
                sum_of_amplitudes = tested_sum_of_amplitudes
                last_best = list_of_others[chosen_model]
                k_j = k_j + 1
            else:
                break
    return last_best


def iteration_step(DOMAIN, domain_values, time_coordinates, frequencies, X, k, structure, params):
    """
    """
    C, U = cl.iteration(X, k, structure, params)
    densities, COV = ca.body(DOMAIN, X, C, U, k, params, structure)
    domain_values_estimation = es.training_model(DOMAIN, C, densities, COV, k, params, structure)
    difference = domain_values - domain_values_estimation
    the_period, sum_of_amplitudes = fm.chosen_period(time_coordinates, difference, frequencies)
    diff = np.sqrt(np.sum(difference ** 2))
    return diff, C, densities, COV, the_period, sum_of_amplitudes











