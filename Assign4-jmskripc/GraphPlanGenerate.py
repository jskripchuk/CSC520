#!/usr/bin/env/python3

"""
James Skripchuk
CSC520
Assignment 4: Extra Credit
"""

import itertools
import sys

# Formats a list into a string to be human readable
def print_list(l):
    s = ""
    for i in l:
        s+=str(i)+", "
    return s[:-2]

# Represents a mutex link between two nodes
class Mutex:
    IE = "Inconsistent Effects"
    IN = "Interference"
    CN = "Competing Needs"
    NL = "Negated Literals"
    IS = "Inconsistent Support"

    def __init__(self, mutex_type ,node_a,node_b):
        self.type = mutex_type
        self.node_a = node_a
        self.node_b = node_b

        self.node_a.mutexes.append(node_b)
        self.node_b.mutexes.append(node_a)

    def __repr__(self):
        return str((self.node_a, self.node_b))

# The GraphPlan graph
class Graph:
    def __init__(self, initial_state, goal_state, actions):
        self.initial_state = initial_state
        self.goal_state = goal_state
        self.actions = actions

        # Set up our first layer
        self.root_layer = Layer(Layer.STATE_LAYER)
        self.root_layer.contents = {i: Node(i,self.root_layer) for i in self.initial_state}
        self.root_layer.depth = 0
        self.last_layer = self.root_layer

        self.depth = 1

        # Build the whole graph
        self.build_graph()

    # Check if two state layers have the same literals and same mutxes
    def leveled_off(self, l1,l2):
        same_literals = str(list(l1.contents.keys()))==str(list(l2.contents.keys()))
        same_negated = str(l1.get_mutex_type(Mutex.NL))==str(l2.get_mutex_type(Mutex.NL))
        same_incon_support = str(l1.get_mutex_type(Mutex.IS))==str(l2.get_mutex_type(Mutex.IS))
        return same_literals and same_negated and same_incon_support

    # Construct the graph until it levels off
    def build_graph(self):
        last_state_level = self.root_layer
        while True:
            # Expand an action layer and then a state layer
            self.expand()
            self.expand()
            current_state_level = self.last_layer

            # Check if the last two state layers have leveled off
            if self.leveled_off(last_state_level,current_state_level):
                break

            last_state_level = current_state_level

    # Print the graph
    def __repr__(self):
        rep = ""
        curr_layer = self.root_layer
        while curr_layer != None:
            rep+=str(curr_layer)+"\n"
            curr_layer = curr_layer.next_layer

        return rep

    # Create an action layer based off of the prev state layer
    def create_action_layer(self):
        new_layer = Layer(Layer.ACT_LAYER)
        
        # Add persistance actions
        perst_actions = {}
        for key,value in self.last_layer.contents.items():
            perst_action = Node(key, new_layer)
            perst_action.effects = [key]
            perst_action.parents.append(value)
            perst_actions[key] = perst_action
        
        new_layer.contents.update(perst_actions)

        # Add actions that could occur in this state
        for _,action in self.actions.items():
            # Does this action have all of it's preconds satisfied?
            satisfied_all_preconds = True 
            for literal in action.preconds:
                if literal not in self.last_layer.contents:
                    satisfied_all_preconds = False
                    break

            # If all the preconds are satisfied
            # Add this action to the current layer
            if satisfied_all_preconds:
                action_node = Node(action.name, new_layer, False)
                action_node.parents = [new_layer.contents[precond] for precond in action.preconds]
                action_node.effects = action.effects
                new_layer.contents[action.name] = action_node

        return new_layer
        
    # Adding a new state layer based off of previous action layer
    def create_state_layer(self):
        new_layer = Layer(Layer.STATE_LAYER)

        # Adding persistant literals
        perst_literals = {}
        for key,value in self.last_layer.contents.items():
            if value.is_literal:
                perst_literal = Node(key, new_layer)
                perst_literal.parents.append(value)
                perst_literals[key] = perst_literal

        new_layer.contents.update(perst_literals)

        # Adding action effects
        for key,value in self.last_layer.contents.items():
            if not value.is_literal:
                effects = self.actions[key].effects

                for effect in effects:

                    # Make sure to not put duplicate effects
                    if effect not in new_layer.contents:
                        effect_node = Node(effect, new_layer)
                    else:
                        effect_node = new_layer.contents[effect]

                    effect_node.parents.append(value)
                    new_layer.contents[effect] = effect_node

        return new_layer

    # Helper function to negate a literal
    def negate(self, literal):
        first = literal[0]
        negation = literal[1:]
        if first == "+":
            negation = "-"+negation
        else:
            negation = "+"+negation

        return negation

    # Given two lists of literals
    # Check if a literal in one list has a negation in the other
    # Eg: [A,B], [C,~B] = True
    # [A,B], [C,B] = False
    def clash(self, l1,l2):
        for literal in l1:
            neg = self.negate(literal)

            if neg in l2:
                return True

        return False

    # See if a certain mutex exists in the current layer
    def mutex_exists(self, layer, m_type, n1, n2):
        for mtx in layer.mutexes:
            if mtx.type == m_type:
                # Make sure to check for symmetric relations [E.g. (A,B) and (B,A)]
                if (mtx.node_a.name==n1 and mtx.node_b.name==n2) or (mtx.node_a.name==n2 and mtx.node_b.name==n1):
                    return True

        return False

    # Mutexes for the state layer
    def add_state_mutexes(self, new_layer):
        # Iterate over all possible combinations of 2 literals
        for s1, s2 in itertools.combinations(new_layer.contents,2):
            s1 = new_layer.contents[s1]
            s2 = new_layer.contents[s2]

            #Negated Literals
            # A literals negation also appears
            if s1.name == self.negate(s2.name):
                new_mutex = Mutex(Mutex.NL, s1,s2)
                new_layer.mutexes.append(new_mutex)
                self.update_mutex_dict(new_layer.mutex_dict, s1,s2, Mutex.NL)

            #Inconsistent Support
            # Each possible pair of actions that could achieve the two literals is mutex
            all_mutexed = True
            for a1 in s1.parents:
                for a2 in s2.parents:
                    # If there is a way to get these that are not mutex
                    if not ((a1.name, a2.name) in a1.layer.mutex_dict or (a2.name, a1.name) in a1.layer.mutex_dict):
                        all_mutexed = False

            #If all possible actions are mutexed, add the IS mutex
            if all_mutexed:
                new_mutex = Mutex(Mutex.IS, s1,s2)
                new_layer.mutexes.append(new_mutex)
                self.update_mutex_dict(new_layer.mutex_dict, s1,s2, Mutex.IS)

    # Add mutex to the mutex dict        
    def update_mutex_dict(self, d, a1, a2, m_type):
        if (a1.name,a2.name) in d:
            d[(a1.name,a2.name)][m_type] = True
        else:
            d[(a1.name,a2.name)] = {}

    # Add mutexes for action layer
    def add_action_mutexes(self, new_layer):
        # Searching for mutexes
        # Iterate over all possible combinations of 2 actions
        for a1, a2 in itertools.combinations(new_layer.contents,2):
            a1 = new_layer.contents[a1]
            a2 = new_layer.contents[a2]

            # Inconsistent effects
            # One action negates the effects of the other
            if self.clash(a1.effects, a2.effects):
                new_mutex = Mutex(Mutex.IE, a1,a2)
                new_layer.mutexes.append(new_mutex)
                self.update_mutex_dict(new_layer.mutex_dict, a1,a2, Mutex.IE)
            
            # Interference 
            #The effects of one action is the negation of a precondition of the other
            #A1 effects and A2 Preconds
            if self.clash(a1.effects, [str(precond) for precond in a2.parents]):
                new_mutex = Mutex(Mutex.IN, a1,a2)
                new_layer.mutexes.append(new_mutex)
                self.update_mutex_dict(new_layer.mutex_dict, a1,a2, Mutex.IN)
            
            #A2 effects and A1 preconds
            #Only do it if they're not both perst actions (avoid double counting)
            if self.clash(a2.effects, [str(precond) for precond in a1.parents]) and not (a1.is_literal and a2.is_literal):
                new_mutex = Mutex(Mutex.IN, a1,a2)
                new_layer.mutexes.append(new_mutex)
                self.update_mutex_dict(new_layer.mutex_dict, a1,a2, Mutex.IN)


            # Competing needs
            # One of the preconditions of one action is mutex with a precondition of the other
            for s1 in a1.parents:
                for s2 in a2.parents:
                    # Mutex found
                    if (s1.name, s2.name) in s1.layer.mutex_dict or (s2.name, s1.name) in a1.layer.mutex_dict:
                        #And it isn't already in current mutex list
                        if not ((a1.name, a2.name) in new_layer.mutex_dict and Mutex.CN in new_layer.mutex_dict[(a1.name, a2.name)]):
                            new_mutex = Mutex(Mutex.CN, a1,a2)
                            new_layer.mutexes.append(new_mutex)
                            self.update_mutex_dict(new_layer.mutex_dict, a1,a2, Mutex.CN)
                            break

    # Make the next layer and add it's mutexes
    def expand(self):
        # Making a new action layer
        if self.last_layer.layer_type == Layer.STATE_LAYER:
            new_layer = self.create_action_layer()
            self.add_action_mutexes(new_layer)
        # Making a new state layer
        else:
            new_layer = self.create_state_layer()
            self.add_state_mutexes(new_layer)


        # Update layer connections
        new_layer.depth = self.depth

        new_layer.prev_layer = self.last_layer
        self.last_layer.next_layer = new_layer
        self.last_layer = new_layer

        self.depth+=1

# Represents a node in the graph plan graph
class Node:
    def __init__(self, name, layer=None, literal=True):
        # Literal vs Action node
        self.is_literal = literal
        self.name = name

        # What layer this node is on
        self.layer = layer

        # Effects and preconds
        self.effects = []
        self.parents = []

        #Any nodes that this node is mutex with
        self.mutexes = []

    def __repr__(self):
        return self.name

# A layer in the graph plan graph
class Layer:
    STATE_LAYER = "StateLayer"
    ACT_LAYER = "ActLayer"

    def __init__(self, layer_type):
        self.depth = 0
        self.layer_type = layer_type
        # All the nodes this is mutex with
        self.mutexes = []
        # A hash table to quickly check if a mutex exists with this node
        self.mutex_dict = {}

        # All the nodes in this layer (literals or actions)
        self.contents = {}
        
        self.next_layer = None
        self.prev_layer = None

    # Get all mutexes based of a certain mutex type
    def get_mutex_type(self, mutex_type):
        return list(filter(lambda m: m.type==mutex_type, self.mutexes))

    # Check if a mutex exists between two nodes in this layer
    def mutex_exists(self, name_1, name_2):
        return (name_1, name_2) in self.mutex_dict or (name_2, name_1) in self.mutex_dict

    # Print out a layer
    def __repr__(self):
        r_string = ""
        if self.layer_type == Layer.STATE_LAYER:
            r_string += "StateLayer: "+str(self.depth//2)+"\n"
            r_string += "\tLiterals: "+print_list(list(self.contents.keys()))
            r_string += "\n\tNegated Literals: "+print_list(self.get_mutex_type(Mutex.NL))
            r_string += "\n\tInconsistent Support:"+print_list(self.get_mutex_type(Mutex.IS))
        else:
            r_string += "ActLayer: "+str(self.depth//2)+"\n"
            r_string += "\tActions:"+print_list(list(self.contents.keys()))
            r_string += "\n\tInconsistent Effects: "+print_list(self.get_mutex_type(Mutex.IE))
            r_string += "\n\tInterference: "+print_list(self.get_mutex_type(Mutex.IN))
            r_string += "\n\tCompeting Needs: "+print_list(self.get_mutex_type(Mutex.CN))

        return r_string

# Represents an action and its effects/preconds
class Action:
    def __init__(self, name):
        self.name = name
        self.preconds = []
        self.effects = []

    def __repr__(self):
        return str((self.name,self.preconds,self.effects))

# Read in our input
def process_input(filepath):
    f = open(filepath, "r")
    strings = f.readlines()
    f.close()

    strings = [line.rstrip("\n") for line in strings]
    strings = [line for line in strings if line]

    initial_state = []
    goal_state = []
    actions = {}

    current_action = None

    # Parse it all
    for line in strings:
        op, conds = line.split(" ")
        conds = conds.strip("[]").split(",")

        if op == "Act":
            current_action = conds[0]
            actions[current_action] = Action(current_action)
        elif op=="Preconditions" or op=="Precondition":
            actions[current_action].preconds = conds
        elif op=="Effects" or op=="Effect":
            actions[current_action].effects = conds
        elif op=="InitialState":
            initial_state = conds
        elif op=="GoalState":
            goal_state = conds

    return initial_state, goal_state, actions


if __name__ == "__main__":
    infile = sys.argv[1]
    outfile = sys.argv[2]

    # Read in our file
    initial_state, goal_state, actions = process_input(infile)

    # Build the graph
    graph = Graph(initial_state, goal_state, actions)

    # Print it out
    f = open(outfile, "w")
    f.write("GraphPlan graph for "+infile+"\n\n"+str(graph))
    f.close()

    print("Graph written to "+outfile)