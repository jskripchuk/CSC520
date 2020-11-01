import itertools

def print_list(l):
    s = ""
    for i in l:
        s+=str(i)+", "
    return s[:-2]

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

class Graph:
    def __init__(self, initial_state, goal_state, actions):
        self.initial_state = initial_state
        self.goal_state = goal_state
        self.actions = actions

        self.root_layer = Layer(Layer.STATE_LAYER)
        self.root_layer.contents = {i: Node(i,self.root_layer) for i in self.initial_state}
        self.root_layer.depth = 0

        self.last_layer = self.root_layer

        self.depth = 1

        self.build_graph()

    def leveled_off(self, l1,l2):
        same_literals = str(list(l1.contents.keys()))==str(list(l2.contents.keys()))
        same_negated = str(l1.get_mutex_type(Mutex.NL))==str(l2.get_mutex_type(Mutex.NL))
        same_incon_support = str(l1.get_mutex_type(Mutex.IS))==str(l2.get_mutex_type(Mutex.IS))
        return same_literals and same_negated and same_incon_support

    def build_graph(self):
        last_state_level = self.root_layer
        while True:
            self.expand()
            self.expand()
            current_state_level = self.last_layer

            if self.leveled_off(last_state_level,current_state_level):
                break

            last_state_level = current_state_level

    def __repr__(self):
        rep = ""
        curr_layer = self.root_layer
        while curr_layer != None:
            #print(curr_layer)
            rep+=str(curr_layer)+"\n"
            curr_layer = curr_layer.next_layer

        return rep

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
        #print(self.actions)

        for _,action in self.actions.items():
            #print(action.preconds)

            # Does this action have all of it's preconds satisfied
            satisfied_all_preconds = True 
            for literal in action.preconds:
                if literal not in self.last_layer.contents:
                    satisfied_all_preconds = False
                    break

            # All the preconds for this action are satisfied
            if satisfied_all_preconds:
                action_node = Node(action.name, new_layer, False)
                action_node.parents = [new_layer.contents[precond] for precond in action.preconds]
                action_node.effects = action.effects
                new_layer.contents[action.name] = action_node

            # Mutexes
        return new_layer
        # Adding a new state layer

    def create_state_layer(self):
        new_layer = Layer(Layer.STATE_LAYER)
        #print("cont",new_layer.contents)

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
                    if effect not in new_layer.contents:
                        effect_node = Node(effect, new_layer)
                    else:
                        effect_node = new_layer.contents[effect]

                    effect_node.parents.append(value)
                    new_layer.contents[effect] = effect_node

        return new_layer

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

    def mutex_exists(self, layer, m_type, n1, n2):
        for mtx in layer.mutexes:
            if mtx.type == m_type:
                if (mtx.node_a.name==n1 and mtx.node_b.name==n2) or (mtx.node_a.name==n2 and mtx.node_b.name==n1):
                    return True

        return False

    def add_state_mutexes(self, new_layer):
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
            # Each possible pair of actions that could achive the two literals is mutex
            all_mutexed = True
            for a1 in s1.parents:
                for a2 in s2.parents:
                    # If there is a way to get these that are not mutex
                    if not ((a1.name, a2.name) in a1.layer.mutex_dict or (a2.name, a1.name) in a1.layer.mutex_dict):
                        all_mutexed = False
                    #print(a1,a2)

            if all_mutexed:
                new_mutex = Mutex(Mutex.IS, s1,s2)
                new_layer.mutexes.append(new_mutex)
                self.update_mutex_dict(new_layer.mutex_dict, s1,s2, Mutex.IS)

                        #print(mtx==act2)
               # pass
                
    def update_mutex_dict(self, d, a1, a2, m_type):
        if (a1.name,a2.name) in d:
            d[(a1.name,a2.name)][m_type] = True
        else:
            d[(a1.name,a2.name)] = {}

    def add_action_mutexes(self, new_layer):
        

        # Searching for mutexes
        for a1, a2 in itertools.combinations(new_layer.contents,2):
            a1 = new_layer.contents[a1]
            a2 = new_layer.contents[a2]
            #print(a1.effects,(a2,a2.effects))

            #for effect in a1.effects:
                

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
                        #if not ((a1.name, a2.name) in new_layer.mutex_dict or (a2.name, a1.name) in new_layer.mutex_dict):
                        if not ((a1.name, a2.name) in new_layer.mutex_dict and Mutex.CN in new_layer.mutex_dict[(a1.name, a2.name)]):
                            new_mutex = Mutex(Mutex.CN, a1,a2)
                            new_layer.mutexes.append(new_mutex)
                            self.update_mutex_dict(new_layer.mutex_dict, a1,a2, Mutex.CN)
                            break


        #print(new_layer.mutexes)

    

    def expand(self):
        # Making a new action layer
        if self.last_layer.layer_type == Layer.STATE_LAYER:
            new_layer = self.create_action_layer()
            self.add_action_mutexes(new_layer)
        else:
            #print("YOO")
            new_layer = self.create_state_layer()
            self.add_state_mutexes(new_layer)

        new_layer.depth = self.depth



        new_layer.prev_layer = self.last_layer
        self.last_layer.next_layer = new_layer
        self.last_layer = new_layer

        self.depth+=1

class Node:
    def __init__(self, name, layer=None, literal=True):
        self.is_literal = literal
        self.name = name
        self.layer = layer
        self.effects = []
        self.parents = []

        #Any nodes that this node is mutex with
        self.mutexes = []

    def __repr__(self):
        return self.name

class Layer:
    STATE_LAYER = "StateLayer"
    ACT_LAYER = "ActLayer"
    def __init__(self, layer_type):
        self.depth = 0
        self.layer_type = layer_type
        self.mutexes = []
        self.mutex_dict = {}
        self.contents = {}
        self.next_layer = None
        self.prev_layer = None

    def get_mutex_type(self, mutex_type):
        return list(filter(lambda m: m.type==mutex_type, self.mutexes))

    def mutex_exists(self, name_1, name_2):
        return (name_1, name_2) in self.mutex_dict or (name_2, name_1) in self.mutex_dict

    

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

def goal(state):
    return False

def expand(state):
    return []

# True if all the goal states are not mutex with eachother
def solution_possible(layer, goal_state):
    for s1, s2 in itertools.combinations(goal_state, 2):
        if layer.mutex_exists(s1,s2):
            return False
    return True



# 
def is_action_set_possible(layer, action_set):
    for a1, a2 in itertools.combinations(action_set, 2):
        if layer.mutex_exists(a1.name,a2.name):
            return False

    return True

class SearchNode:
    def __init__(self, literal_set={}):
        self.literal_set = literal_set
        self.action_set = {}
        self.parent = None

    def __repr__(self):
        return str(self.literal_set)

def extract_layer(curr_layer, goal_node, init_set):
    goal_state = goal_node.literal_set

    if goal_state == init_set:
        return goal_node
    
    if solution_possible(curr_layer, goal_state):
        x = [curr_layer.contents[lit].parents for lit in goal_state]
        possible_actions = []
        
        for z in itertools.product(*x):
            if is_action_set_possible(curr_layer.prev_layer,z):
                req_preconds = {}
                for action in z:
                    req_preconds.update({str(s):True for s in action.parents})

                prev_node = SearchNode(req_preconds)
                prev_node.action_set = {str(act) for act in z}
                prev_node.parent = goal_node

                return extract_layer(curr_layer.prev_layer.prev_layer, prev_node, init_set)

        #print(possible_actions)

    return False

def extract_plan(graph):
    goal_set = {x:True for x in graph.goal_state}
    init_set = {str(x):True for x in graph.initial_state}

    curr_layer = graph.last_layer
    goal_states = SearchNode(goal_set)

    plan_root = extract_layer(curr_layer,goal_states,init_set)
    
    current_step = plan_root

    print_str = ""
    step_num = 0
    while True:
        print_str+="Step: "+str(step_num)
        if current_step.literal_set == goal_set:
            print_str+= "\n\tGoal: "+print_list([x for x in current_step.literal_set.keys()])
            break
        else:
            print_str+= "\n\tCurrent Literals: "+print_list([x for x in current_step.literal_set.keys()])
            
            no_persist = []
            for z in [str(x) for x in current_step.action_set]:
                if not (z[0]=="+" or z[0]=="-"):
                    no_persist.append(z)

            print_str+="\n\tTake Actions: "+print_list(no_persist)
            print_str+="\n"

        if current_step.parent == None:
            break
        

        current_step = current_step.parent
        step_num+=1
    print(print_str)

if __name__ == "__main__":
    infile = "./Problems/ProblemB.txt"
    initial_state, goal_state, actions = process_input(infile)
    graph = Graph(initial_state, goal_state, actions)
    #print(graph)
    extract_plan(graph)