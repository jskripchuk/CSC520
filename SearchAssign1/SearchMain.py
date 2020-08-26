"""
James Skripchuk
CSC520
Assignment 1
"""

class CityNode:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.adjacent = []
        
        #Used for A*
        self.cost = 0

    def __str__(self):
        return "{0},{1},{2},{3}".format(self.name,self.latitude,self.longitude,self.adjacent)
    
    def __repr__(self):
        return "{0},{1},{2},{3}".format(self.name,self.latitude,self.longitude,self.adjacent)

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return self.name==other.name

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    # Add a node to the Graph
    def add_node(self, name,latitude,longitude):
        self.nodes[name] = CityNode(name,latitude,longitude)

    def sort_edges(self, reverse):
        for name in self.nodes.keys():
            n = self.nodes[name]
            n.adjacent.sort()
            if reverse:
                n.adjacent.reverse()

    def zero_costs(self):
        for name in self.nodes.keys():
            n = self.nodes[name]
            n.cost = 0


    # Add an edge between nodes a and b with distance d
    # Assume edges are bidirectional
    def add_edge(self, a, b, dist):
        try:
            self.nodes[a].adjacent.append((b, dist))
            self.nodes[b].adjacent.append((a,dist))

            self.edges[(a,b)]=dist
            self.edges[(b,a)]=dist
        except:
            print("Error connecting {0} and {1}, does one of these cities exist?".format(a,b))
        

    def __str__(self):
        return str(self.nodes)

def parse(inputfile):
    f = open(inputfile)
    
    lines = f.readlines()
    f.close()

    lines = [x.strip() for x in lines]
    lines = [x.replace(" ","") for x in lines]
    lines = lines[6:]
    lines = list(filter(None,lines))

    #print(lines)

    locations = []
    dists = []

    for i in range(len(lines)):
        if lines[i][0]=="%":
            locations = lines[0:i]
            dists = lines[i+1:]
            break

    locations = [[x for x in i.split(",")] for i in locations]
    dists = [[x for x in i.split(",")] for i in dists]

    return locations,dists
        
def build_graph(locations, dists):
    graph = Graph()
    for loc in locations:
        graph.add_node(loc[0], float(loc[1]),float(loc[2]))

    for dist in dists:
        source = dist[0]
        dest = dist[1]
        d = dist[2]
        graph.add_edge(source,dest,float(d))

    #print(graph)
    return graph


def trace_back(dest,discovered,graph):
    path = [dest]
    cur = discovered[dest]

    #print(discovered)

    total_cost = graph.edges[(dest,discovered[dest])]

    while cur != "":
        path.append(cur)

        if discovered[cur]:
            total_cost+=graph.edges[(cur,discovered[cur])]

        cur = discovered[cur]

    path.reverse()

    path_str = ""
    for i in path:
        path_str+=i+"->"
    path_str = path_str[:-2]
    #print(total_cost)

    return path_str,total_cost


import queue

class OpenSet():
    def __init__(self,mode):
        self.mode = mode
        self.queue = queue.Queue()
        self.stack = []

    def put(self, object):
        if self.mode == "queue":
            return self.queue.put(object)
        else:
            return self.stack.append(object)

    def get(self):
        if self.mode =="queue":
            return self.queue.get()
        else:
            return self.stack.pop()

    def empty(self):
        if self.mode =="queue":
            return self.queue.empty()
        else:
            return len(self.stack)==0

    def get_set(self):
        if self.mode == "queue":
            return self.queue.queue
        else:
            return self.stack


    
def bfs(graph,source,dest):
    return uninformed_search(graph,source,dest,"queue")

def dfs(graph,source,dest):
    print("DFS")
    return uninformed_search(graph,source,dest,"stack")

def uninformed_search(graph, source, dest, mode="queue"):
    resp = ""
    if mode=="queue":
        resp="BFS"
    else:
        resp = "DFS"

    log_string = "You have selected {0}\n".format(resp)

    #frontier = queue.Queue()
    frontier = OpenSet(mode)
    discovered = {}

    frontier.put(graph.nodes[source])
    discovered[source] = ""
    found = False
    nodes_expanded = 0


    #Get top of queue
    while not frontier.empty():
        v = frontier.get()
        log_string+="Expanding city: {0}\n".format(v.name)
        nodes_expanded+=1

        if v.name == dest:
            log_string+="{0} has been found!\n".format(dest)
            found = True
            log_string+="==============\n"
            break
        else:

            adjacent = []
            for edge in v.adjacent:
                edge_name = edge[0]
                if edge_name not in discovered:
                    frontier.put(graph.nodes[edge[0]])
                    adjacent.append(edge_name)
                    discovered[edge_name] = v.name

        log_string+="Adding to the frontier: {0}\n".format(adjacent)
        frontier_names = []
        for i in frontier.get_set():
            frontier_names.append(i.name)

        log_string+="The frontier is now: {0}\n".format(frontier_names)
        log_string+="==============\n"
    
    #Trace back the path
    if found:
        path_str,total_cost=trace_back(dest,discovered,graph)

        log_string+="Your final route is:\n"
        log_string+=path_str+"\n"
        log_string+="The total cost is:\n"
        log_string+=str(total_cost)
        print(log_string)

        return path_str, total_cost, nodes_expanded
    else:
        log_string+="No route has been found.\n"
        return (0,0,0)
        

    #print(log_string)


import heapq


#all we need to do now is add heuristicssssss
def astar(graph, source, dest, heuristic):
    frontier = []
    frontier_set = {}
    discovered = {}

    nodes_expanded = 0

    found = False

    discovered[source] = ""
    heapq.heappush(frontier, (0,graph.nodes[source]))
    frontier_set[source]=True
    log_string=""


    while frontier:
        v = heapq.heappop(frontier)
        node = v[1]
        frontier_set.pop(node.name)
        log_string+="Expanding city: {0} with cost {1}\n".format(node.name,v[0])
        nodes_expanded+=1

        if node.name == dest:
            log_string+="{0} has been found!\n".format(dest)
            found = True
            log_string+="==============\n"
            #print("FOUND IT")
            break
        else:
            adjacent = []

            for edge in node.adjacent:
                edge_name = edge[0]
                h_distance = heuristic(edge_name, dest, graph)
                #print("Actual Distance: {0}, H Distance: {1}".format(edge[1],h_distance))
                current_cost = node.cost + edge[1]
                adjacent.append(edge_name)

                if edge_name not in discovered and edge_name not in frontier_set:
                    graph.nodes[edge_name].cost = current_cost
                    heapq.heappush(frontier, (current_cost+h_distance,graph.nodes[edge_name]))
                    
                    discovered[edge_name] = node.name
                    frontier_set[edge_name] = True
                    #adjacent.append(edge_name)
                    #discovered[edge_name] = v.name

                #We found a better path to this node
                if edge_name in frontier_set:
                    if current_cost < graph.nodes[edge_name].cost:
                        for i in range(len(frontier)):
                            if frontier[i][1].name == edge_name:
                                frontier.pop(i)
                                break

                        graph.nodes[edge_name].cost = current_cost
                        discovered[edge_name] = node.name
                        heapq.heappush(frontier, (current_cost+h_distance,graph.nodes[edge_name]))
                        
                
            
            log_string+="Adding to the frontier: {0}\n".format(adjacent)

            sort_front = sorted([(x[0],x[1].name) for x in frontier])

            log_string+="The frontier is now: {0}\n".format(sort_front)
            log_string+="==============\n"
    
    #Trace back the path
    if found:
        path_str,total_cost=trace_back(dest,discovered,graph)

        log_string+="Your final route is:\n"
        log_string+=path_str+"\n"
        log_string+="The total cost is: {0}\n".format(total_cost)
        log_string+="The total number of nodes expanded was: {0}\n".format(nodes_expanded)
        #print(log_string)
        return path_str,total_cost, nodes_expanded
    else:
        log_string+="No route has been found.\n"
        return 0,0,0
        
    
def zero_heuristic(node_name, dest,graph):
    return 0

import math
def straight_heuristic(source_name,dest_name,graph):
    #sqrt((69.5 * (Lat1 - Lat2)) ^ 2 + (69.5 * cos((Lat1 + Lat2)/360 * pi) * (Long1 - Long2)) ^ 2)
    lat1 = graph.nodes[source_name].latitude
    lat2 = graph.nodes[dest_name].latitude

    long1 = graph.nodes[source_name].longitude
    long2 = graph.nodes[dest_name].longitude

    #print(source_name)
    #print(lat1,long1)
    #print(dest_name)
    #print(lat2,long2)


    dist = math.sqrt( (69.5 * (lat1 - lat2))**2 + (69.5 * math.cos((lat1 + lat2)/360 * math.pi) * (long1 - long2))**2 )
    #print(math.pi)
    return dist
    
import random


# Because I had a hunch that due to the non-consistancy of the heursitic
# Also I was too lazy to find a counterexample by hand
def random_search(graph):
    while True:
        source = random.choice(list(graph.nodes.keys()))
        dest = random.choice(list(graph.nodes.keys()))

        if source != dest:
            a = astar(graph,source,dest,straight_heuristic)
            graph.zero_costs()
            b = astar(graph,dest,source,straight_heuristic)
            graph.zero_costs()
            #print(source,dest)
            #print(a[1],b[1])
            #print("============")
            if a[1] != b[1]:
                print(a[0])
                print(b[0])
                break

def euclid_dist(source_name,dest_name,graph):
    lat1 = graph.nodes[source_name].latitude
    lat2 = graph.nodes[dest_name].latitude

    long1 = graph.nodes[source_name].longitude
    long2 = graph.nodes[dest_name].longitude

    return math.sqrt((lat1-lat2)**2+(long1+long2)**2)

def astar_different_path_case():
    g = Graph()
    g.add_node("A",0,0)
    g.add_node("B",2,1)
    g.add_node("C",1,1)
    g.add_node("D",1,-1)
    g.add_node("E",2,-1)
    g.add_node("F",3,0)

    g.add_edge("A","C",1)
    g.add_edge("A","D",1)

    g.add_edge("C","E",1)
    g.add_edge("D","B",1)

    g.add_edge("E","F",1)
    g.add_edge("B","F",1)
   
    g.sort_edges(False)
    path, cost, nodes_expanded = astar(g,"A","F",euclid_dist)
    g.zero_costs()
    print(path)

    path, cost, nodes_expanded = astar(g,"F","A",euclid_dist)
    print(path)

import sys

if __name__ == "__main__":

    searchtype = sys.argv[1]
    inputfile = sys.argv[2]
    startcity = sys.argv[3]
    endcity = sys.argv[4]
    outputfile = sys.argv[5]

    locations, dists = parse(inputfile)
    graph = build_graph(locations,dists)
    #Put all adjacency lists in alphabetical order for consistancy
    
    #random_search(graph)

    

    if searchtype=="bfs":
        graph.sort_edges(False)
        path, cost, nodes_expanded = bfs(graph,startcity,endcity)
    elif searchtype=="dfs":
        graph.sort_edges(True)
        path, cost, nodes_expanded = dfs(graph,startcity,endcity)
    elif searchtype=="astar":
        graph.sort_edges(False)
        path, cost, nodes_expanded = astar(graph,startcity,endcity,straight_heuristic)
    
    

    print("Path:", path)
    print("Total Cost:", cost)
    print("Nodes Expanded:", nodes_expanded)
    #astar_different_path_case()

    

    

    #print("Heuristic Distance:",straight_heuristic("vancouver","seattle",graph))
    #print("Actual Distance:",graph.edges[("vancouver","seattle")])
