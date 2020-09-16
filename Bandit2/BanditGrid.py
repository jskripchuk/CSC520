#!/usr/bin/env/python3

"""
James Skripchuk
CSC520
Assignment 2: Extra Credit
"""

from BanditAlg import bandit, process_input
import sys 
import math
import numpy as np

def grid_search(col_names, data, max_iter, step):
    num_iters = 0
    best_score = -math.inf
    best_params = {}
    log_string = ""

    # I don't interate over the uniform distribution because
    # that doesn't really make any mathematical sense.
    # The entire distribution should add up to one,
    # so the value must be 1/N
    dist = 1/len(col_names)
    
    w0_max = 100

    # Iterate the paramaters!
    for w0 in np.arange(1,w0_max,step):
        for exp in np.arange(0,1,step):
            for decay in np.arange(0,1,step):
                for rwt in np.arange(0,1,step):

                    if num_iters > max_iter:
                        break
                    
                    num_iters+=1
                    
                    params = {
                        "exp": exp,
                        "dist": dist,
                        "decay": decay,
                        "rwt": rwt,
                        "w0": w0
                    }
                    
                    # Run the bandit
                    score,_,_,run_log = bandit(params, col_names, data)
                    row = "** Start {0},{1},{2},{3},{4},{5} **".format(
                        num_iters,
                        exp,
                        dist,
                        decay,
                        rwt,
                        w0
                    )
                    print(row)
                    log_string+=row+"\n"
                    log_string+=run_log


                    if score > best_score:
                        best_score = score
                        best_params = params

    return best_score, best_params, log_string

if __name__ == "__main__":
    max_iter = int(sys.argv[1])
    step = float(sys.argv[2])
    infile = sys.argv[3]
    outfile = sys.argv[4]

    col_names, data = process_input(infile)

    # Perform the grid search
    best_score, best_params, log_string = grid_search(col_names, data, max_iter, step)
    best_str = "** BestScore, {0},{1},{2},{3},{4},{5} **".format(
        best_params["exp"],
        best_params["dist"],
        best_params["decay"],
        best_params["rwt"],
        best_params["w0"],
        best_score
    )

    log_string+=best_str

    print(best_str)

    f = open(outfile, "w")
    f.write(log_string)
    f.close()
