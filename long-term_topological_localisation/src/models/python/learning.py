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

import model as mdl
import fremen as fm
import initialization as init
import dataset_io as dio
import evaluation as ev

def proposed_method(longest, shortest, dataset, edges_of_cell, k,
                    radius, number_of_periods, evaluation):
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
    # initialization
    training_data, evaluation_dataset, training_dataset =\
        dio.divide_dataset(dataset)
    input_coordinates, overall_sum, structure, C, U,\
        shape_of_grid, time_frame_sums, T, W, ES, P, COV,\
        density_integrals, valid_timesteps =\
        init.whole_initialization(training_data, k, edges_of_cell,
                                  longest, shortest, training_dataset)
    # initialization of fiff, probably better inside  "whole_initialization"
    diff = -1
    # iteration
    if len(structure[1]) >= number_of_periods:
        jump_out = 1
    else:
        jump_out = 0
    iteration = 0
    while jump_out == 0:
        iteration += 1
        print('\nstarting learning iteration: ' + str(iteration))
        start = clock()
        if evaluation:
            jump_out, structure, C, U, COV, density_integrals, W, ES, P, diff=\
                step_evaluation(training_data, input_coordinates, structure,
                                C, U, k, shape_of_grid, time_frame_sums, T, W,
                                ES, COV, density_integrals, P, radius,
                                valid_timesteps,
                                evaluation_dataset, edges_of_cell, diff)
        else:
            structure[2].append(P)
            if len(structure[2]) == 1:
                structure[1].append(radius)
            else:
                #structure[1].append(structure[1][-1] *
                #                    structure[2][-2] / structure[2][-1])
                structure[1].append(radius)
            dES, structure, C, U, COV, density_integrals, W, ES, P, diff =\
                iteration_step(training_data, input_coordinates, structure, C,
                               U, k, shape_of_grid, time_frame_sums, T, W, ES,
                               valid_timesteps,
                               evaluation_dataset, edges_of_cell, diff)
            jump_out = 0
        if len(structure[1]) >= number_of_periods:
            jump_out = 1
        finish = clock()
        print('structure: ' + str(structure))
        print('leaving learning iteration: ' + str(iteration))
        print('processor time: ' + str(finish - start))
    print('learning iterations finished')
    average = overall_sum / len(input_coordinates)
    return C, COV, density_integrals, structure, average


def step_evaluation(training_data, input_coordinates, structure, C, U, k,
                    shape_of_grid, time_frame_sums, T, W, ES, COV,
                    density_integrals, P, radius, valid_timesteps,
                    evaluation_dataset, edges_of_cell, diff_old):
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
    new_structure[2].append(P)
    if len(new_structure[2]) == 1:
        new_structure[1].append(radius)
    else:
        #new_structure[1].append(new_structure[1][-1] *
        #                        new_structure[2][-2] / new_structure[2][-1])
        new_structure[1].append(radius)
        print('pridal jsem radius')
    full_output = iteration_step(training_data, input_coordinates,
                                 new_structure, C, U, k, shape_of_grid,
                                 time_frame_sums, T, W, ES, valid_timesteps,
                                 evaluation_dataset, edges_of_cell, diff_old)
    if full_output[-1] < diff_old or diff_old == -1:  # (==) if diff < diff_old
        dES, structure, C, U, COV, density_integrals, W, ES, P, diff\
            = full_output
        jump_out = 0
    else:
        jump_out = 1
        diff = diff_old
        print('\ntoo many periodicities, error have risen,')
        print('when structure ' + str(new_structure) + ' tested;')
        print('jumping out (prematurely)\n')
    return jump_out, structure, C, U, COV, density_integrals, W, ES, P, diff


def iteration_step(training_data, input_coordinates, structure, C_old, U_old,
                   k, shape_of_grid, time_frame_sums, T, W, ES,
                   valid_timesteps, evaluation_dataset, edges_of_cell,
                   diff_old):
    """
    input: path string, path to file
           input_coordinates numpy array, coordinates for model creation
           structure list(int, list(floats), list(floats)),
                      number of non-hypertime dimensions, list of hypertime
                      radii nad list of wavelengths
           C_old numpy array kxd, centres from last iteration
           U_old numpy array kxn, matrix of weights from the last iteration
           k positive integer, number of clusters
           shape_of_grid numpy array dx1 int64, number of cells in every
                                                dimension
           time_frame_sums numpy array shape_of_grid[0]x1, sum of measures
                                                            over every
                                                            timeframe
           T numpy array shape_of_grid[0]x1, time positions of timeframes
           W numpy array Lx1, sequence of reasonable frequencies
           ES float64, squared sum of squares of residues from this iteration
    output: dES float64, difference between last and new error
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
    uses: mdl.model_creation(), fm.chosen_period()
          np.sum()
    objective:
    """
    #### testuji zmenu "sily" period pri pridavani shluku
    hist_freqs, C, U, COV, density_integrals =\
        mdl.model_creation(input_coordinates,
                           structure, training_data, C_old, U_old, k,
                           shape_of_grid)
    osy = tuple(np.arange(len(np.shape(hist_freqs)) - 1) + 1)
    time_frame_freqs = np.sum(hist_freqs, axis=osy)
    P, W, ES, dES = fm.chosen_period(T, time_frame_sums,
                                     time_frame_freqs, W, ES, valid_timesteps)
    diff = ev.evaluation_step(evaluation_dataset, C, COV, density_integrals,\
                           structure, k, edges_of_cell)
    #for i in xrange(k, k+5):
    #    for j in xrange(5):
    #        print('pokus: ' + str(j))
    #        print('k: ' + str(i))
    #        hist_freqs, C, U, COV, density_integrals =\
    #            mdl.model_creation(input_coordinates,
    #                               structure, training_data, C_old, U_old, i,
    #                               shape_of_grid)
    #        osy = tuple(np.arange(len(np.shape(hist_freqs)) - 1) + 1)
    #        time_frame_freqs = np.sum(hist_freqs, axis=osy)
    #        P, W, ES, dES = fm.chosen_period(T, time_frame_sums,
    #                                         time_frame_freqs, W, ES, valid_timesteps)
    #        diff = ev.evaluation_step(evaluation_dataset, C, COV, density_integrals,\
    #                                  structure, k, edges_of_cell)
    #### konec testovani
    print('for structure:')
    print(structure)
    return dES, structure, C, U, COV, density_integrals, W, ES, P, diff
