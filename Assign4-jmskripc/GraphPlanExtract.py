#!/usr/bin/env/python3

"""
James Skripchuk
CSC520
Assignment 4: Extra Credit
"""

import itertools
import sys
from GraphPlanGenerate import Graph, print_list, process_input

# True if all the goal states are not mutex with eachother
def solution_possible(layer, goal_state):
    # For every 2-combination of states, make sure they're consistent
    for s1, s2 in itertools.combinations(goal_state, 2):
        if layer.mutex_exists(s1,s2):
            return False
    return True

# Make sure that a given set of actions is actually possible
def is_action_set_possible(layer, action_set):
    # Check all 2-combinations of actions
    # And make sure they're all not mutexes
    for a1, a2 in itertools.combinations(action_set, 2):
        if layer.mutex_exists(a1.name,a2.name):
            return False

    return True

# Wrapper for reprenting a node in the search space for the solution
class SearchNode:
    def __init__(self, literal_set={}):
        self.literal_set = literal_set
        self.action_set = {}
        self.parent = None

    def __repr__(self):
        return str(self.literal_set)

# Try and extract a solution starting of this layer
def extract_layer(curr_layer, goal_node, init_set):
    # Look at our current goals
    goal_state = goal_node.literal_set

    # If they matched our initial set of goals, we found our solution!
    if goal_state == init_set:
        return goal_node
    
    # First check if a solution is even possible (check mutxes)
    if solution_possible(curr_layer, goal_state):
        preconds = [curr_layer.contents[lit].parents for lit in goal_state]
        possible_actions = []
        
        # For every possible set of actions that could lead up to this state
        for action_set in itertools.product(*preconds):
            # Check to see if it's possible for this to occur
            # (no mutxes between any tow actions)
            if is_action_set_possible(curr_layer.prev_layer,action_set):

                #Update the preconds required for this action set
                req_preconds = {}
                for action in action_set:
                    req_preconds.update({str(s):True for s in action.parents})

                prev_node = SearchNode(req_preconds)
                prev_node.action_set = {str(act) for act in action_set}
                prev_node.parent = goal_node

                # Recurse! See if we can get a solution with this action set
                res = extract_layer(curr_layer.prev_layer.prev_layer, prev_node, init_set)
                
                # If this returns a successful solution, return it
                if res:
                    return res
                # Otherwise keep looping though possible sets of actions
                # That could get us to this state

    # If we run out of possible actions, return failure
    return None

def extract_plan(graph):
    # Get our goal and initial states
    goal_set = {x:True for x in graph.goal_state}
    init_set = {str(x):True for x in graph.initial_state}

    curr_layer = graph.last_layer
    goal_states = SearchNode(goal_set)

    # Try and extract a plan
    plan_root = extract_layer(curr_layer,goal_states,init_set)
    
    current_step = plan_root

    
    # Loop though our solution and print out results
    print_str = "\nPersistance actions have been removed for simplicity.\n\n"
    step_num = 0
    while True:
        print_str+="Step: "+str(step_num)
        if current_step.literal_set == goal_set:
            # print goal set
            print_str+= "\n\tGoal: "+print_list([x for x in current_step.literal_set.keys()])
            break
        else:
            # Print literals that are active at this level
            print_str+= "\n\tCurrent Literals: "+print_list([x for x in current_step.literal_set.keys()])
            
            # Remove persistant actions
            no_persist = []
            for z in [str(x) for x in current_step.action_set]:
                if not (z[0]=="+" or z[0]=="-"):
                    no_persist.append(z)

            # Print what actions need to be taken at this level
            print_str+="\n\tTake Actions: "+print_list(no_persist)
            print_str+="\n"

        if current_step.parent == None:
            break
        

        current_step = current_step.parent
        step_num+=1
        
    return print_str

if __name__ == "__main__":
    infile = sys.argv[1]
    outfile = sys.argv[2]

    # Read our input
    initial_state, goal_state, actions = process_input(infile)

    # Build our graph
    graph = Graph(initial_state, goal_state, actions)

    # Try and extract a plan
    try:
        plan = extract_plan(graph)
        print("Plan Found!")
    except:
        print("No Plan Found...")
        plan = "\nNo Plan"
    
    # Print it out
    f = open(outfile, "w")
    f.write("Solution plan for "+infile+str(plan))
    f.close()

    print("Solution written to "+outfile)