#!/usr/bin/env/python3

"""
James Skripchuk
CSC520
Assignment 2
"""

import csv
import random
import math
import sys

# Return the column names and all of our data rows
def process_input(infile):
    with open(infile, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        table = [row for row in csv_reader]
        col_names = table[0]
        data = table[1:]

    data = [[int(x) for x in row] for row in data]
    return col_names, data

# Normalize a list of values to be between [0,1]
# Min-Max feature scaling
def min_max_normalize(l):
    min_value = min(l)
    max_value = max(l)
    diff = max_value-min_value

    # This is to avoid glitches on the first round where everything is uniformly distributed
    if diff==0:
        diff=1

    return [(x-min_value)/(diff) for x in l]

# Another function that not only normalizes numbers > 0
# but also makes sure that the sum equals 1 
def normalize(l):
    total = sum(l)

    # Again, to prevent glitches on the first round
    # If the total is 0, just return a uniform distribution
    if total == 0:
        return [1/len(l) for i in l]

    return [x/total for x in l]

# Main bandit code
def bandit(params, col_names, data):

    # Set all of our initial weights to the w0
    weights = [params['w0'] for w in range(len(col_names))]

    total_reward = 0

    log_string = ""
    
    # Go though all of our data rows
    for i, current_row in enumerate(data):
        # Normalize our weights
        norm_weights = min_max_normalize(weights)

        # Caculate the probabilities
        probabilities = [(w*(1-params['exp']) + params['exp']*params['dist']) for w in norm_weights]
        probabilities = normalize(probabilities)
        
        # Select an action based off of the weighted probabilities
        action = random.choices(range(0,len(col_names)), weights=probabilities)[0]

        # Take our action
        reward = current_row[action]
        total_reward+=reward

        # Update the weight of that action
        weights[action] = params['decay']*weights[action]+params['rwt']*reward

        log_string += "{0},{1},{2},{3}".format(i, col_names[action], reward, total_reward)
        for j in range(len(weights)):
            log_string+=",{0},{1}".format(probabilities[j],weights[j])
        log_string+="\n"

    return total_reward, weights, probabilities, log_string

if __name__ == "__main__":
    exp = float(sys.argv[1])
    dist = float(sys.argv[2])
    decay = float(sys.argv[3])
    rwt = float(sys.argv[4])
    w0 = float(sys.argv[5])
    infile = sys.argv[6]
    outfile = sys.argv[7]

    col_names, data = process_input(infile)
    
    """
    params = {
        "exp": 0.01,
        "dist": 1/len(col_names),
        "decay": 0.7,
        "rwt": 0.5,
        "w0": 10
    }
    """

    params = {
        "exp": exp,
        "dist": dist,
        "decay": decay,
        "rwt": rwt,
        "w0": w0
    }

    r, w, p, log_string = bandit(params, col_names, data)
    print("Total Reward:",r)

    f = open(outfile, "w")
    f.write(log_string)
    f.close()



"""
BEGIN SCRATCH WORK ZONE

This is just some helper code that I used to generate
the data for the graphs for question 4.

def decay_mod(col_names, data):
    decays = []
    avg_runs = []

    for dec in np.arange(0,1,0.01):
        print(dec)
        runs = []

        for i in range(0,10):
            params = {
                "exp": 0.05,
                "dist": 1/len(col_names),
                "decay": 0.7,
                "rwt": dec,
                "w0": 10,
                "outfile": "./out.txt"
            }
    
            runs.append(bandit(params, col_names, data))

        print(runs)
        decays.append(dec)
        avg_runs.append(sum(runs)/len(runs))


    print(decays)
    print(avg_runs)

    with open('./rwd_rate_B.csv', mode='w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for i in range(len(decays)):
            writer.writerow([decays[i],avg_runs[i]])

END SCRATCH WORK ZONE
"""