class Mutex:
    def __init__(self, mutex_type ,a,b):
        self.type = mutex_type
        self.a = a
        self.b = b

class Graph:
    def __init__(self, initial_state, goal_state, actions):
        self.initial_state = initial_state
        self.goal_state = goal_state
        self.actions = actions

        self.STATE_LAYER = "StateLayer"
        self.ACT_LAYER = "ActLayer"

        self.root_layer = Layer(self.STATE_LAYER)
        self.root_layer.contents = {i: Node(i,self.root_layer) for i in self.initial_state}

        self.last_layer = self.root_layer

        self.expand()

        print(self)

    def build_graph(self):
        pass

    def __repr__(self):
        rep = ""
        curr_layer = self.root_layer
        while curr_layer != None:
            #print(curr_layer)
            rep+=str(curr_layer)+"\n"
            curr_layer = curr_layer.next_layer

        return rep

    def expand(self):

        # Making a new action layer
        if self.last_layer.layer_type == self.STATE_LAYER:
            new_layer = Layer(self.ACT_LAYER)
            # Add persistance actions
            perst_actions = {}
            for key,value in self.last_layer.contents.items():
                perst_action = Node(key, new_layer)
                perst_action.parents.append(value)
                perst_actions[key] = perst_action
            
            new_layer.contents.update(perst_actions)

            # Add actions that could occur in this state
            #print(self.actions)

            for _,action in self.actions.items():
                print(action.preconds)

        else:
            pass

        new_layer.prev_layer = self.last_layer
        self.last_layer.next_layer = new_layer
        self.last_layer = new_layer

class Node:
    def __init__(self, name, layer=None):
        self.name = name
        self.layer = layer
        self.parents = []
        self.mutexes = []

    def __repr__(self):
        return self.name

class Layer:
    def __init__(self, layer_type, contents={}):
        self.layer_type = layer_type
        self.contents = contents
        self.next_layer = None
        self.prev_layer = None

    def __repr__(self):
        return self.layer_type+": "+str(self.contents)

class Action:
    def __init__(self, name):
        self.name = name
        self.preconds = []
        self.effects = []

    def __repr__(self):
        return str((self.name,self.preconds,self.effects))

def process_input(filepath):
    f = open(filepath, "r")
    strings = f.readlines()
    f.close()

    strings = [line.rstrip("\n") for line in strings]
    strings = [line for line in strings if line]

    initial_state = []
    goal_state = []
    actions = {}

    #print(s)
    current_action = None
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
    #print("Starting Graphplan")
    infile = "./Problems/ProblemA.txt"
    initial_state, goal_state, actions = process_input(infile)
    graph = Graph(initial_state, goal_state, actions)