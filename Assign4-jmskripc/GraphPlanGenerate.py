
class StateLayer:
    def __init__(self):
        pass

class Literal:
    pass

class Action:
    pass

class ActionLayer:
    pass

class Mutex:
    pass

def process_input(filepath):
    f = open(filepath, "r")
    strings = f.readlines()
    f.close()

    strings = [line.rstrip("\n") for line in strings]
    strings = [line for line in strings if line]

    #print(s)
    for line in strings:
        op, conds = line.split(" ")
        print(op,conds)

if __name__ == "__main__":
    #print("Starting Graphplan")
    infile = "./Problems/ProblemA.txt"
    process_input(infile)