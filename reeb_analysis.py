from math import sqrt
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import matplotlib.collections as mc
from matplotlib.colors import LogNorm
import numpy as np
from joblib import Parallel, delayed
import networkx as nx

# Fetch all the files
print("Enumerating files...")
OBJ_PATH = 'reeb_exports'
files = sorted([join(OBJ_PATH, f) for f in listdir(OBJ_PATH) if isfile(join(OBJ_PATH, f))])

# Parse all files into reeb graph objects
print("Parsing all files...")
timesteps = []
for file in files:
    content = open(file, "r")
    nodes = []
    edges = []
    for line in content:
        if (str(line).startswith('v')):
            split = str(line).split(' ')
            node = (float(split[1]), float(split[2]))
            nodes.append(node)
        elif (str(line).startswith('l')):
            split = str(line).split(' ')
            edge = (int(split[1]) - 1, int(split[2]) - 1)
            edges.append(edge)
    timesteps.append({'nodes': nodes, 'edges': edges, 'file': file})

# Compute the critical points and types
print("Computing critical types...")
critical_types = ['minimum', 'split', 'merge', 'maximum', 'none']
def compute_critical(reeb_graph):
    nodes = reeb_graph['nodes']
    edges = reeb_graph['edges']
    types = [4 for i in range(len(nodes))]
    for id in range(len(nodes)):
        node = nodes[id]
        adjacent_edges = list(filter(lambda edge: edge[0] == id or edge[1] == id, edges))
        adjacent_nodes = []
        for edge in adjacent_edges:
            if edge[0] != id:
                adjacent_nodes.append(edge[0])
            elif edge[1] != id:
                adjacent_nodes.append(edge[1])
        # Check minimum type
        if node[0] <= min([nodes[n][0] for n in adjacent_nodes]):
            types[id] = 0
        # Check maximum type
        elif node[0] >= max([nodes[n][0] for n in adjacent_nodes]):
            types[id] = 3
        # Check split node
        elif len(list(filter(lambda n: nodes[n][0] > node[0], adjacent_nodes))) > 1:
            types[id] = 1
        # Check merge node
        elif len(list(filter(lambda n: nodes[n][0] < node[0], adjacent_nodes))) > 1:
            types[id] = 2
        elif len(list(filter(lambda n: nodes[n][0] < node[0], adjacent_nodes))) > 1: types[id] = 2
    return {'name': reeb_graph['file'], 'types': types}

types = Parallel(n_jobs=8)(delayed(compute_critical)(reeb) for reeb in timesteps)
for type in types:
    for step in timesteps:
        if step['file'] == type['name']:
            step['types'] = type['types']
            break
print("Data preparation done!")

def count_parallel_channels():
    count = [[] for t in range(len(timesteps))]
    for t in range(len(timesteps)):
        reeb = timesteps[t]
        ranges = list(map(lambda e: (reeb['nodes'][e[0]][0], reeb['nodes'][e[1]][0]), reeb['edges']))
        for r in ranges:
            if r[0] > r[1]: r = reversed(r)
        count[t] = [0 for x in range(1600)]
        for r in ranges:
            for x in range(int(r[0]), int(r[1])): count[t][x] += 1
    plt.imshow(count, origin='lower')
    plt.xlabel('Distance from river origin')
    plt.ylabel('Timestep')
    plt.colorbar()
    plt.show()

def count_components():
    num_components = []
    for reeb in timesteps:
        G = nx.Graph()
        G.add_nodes_from(range(len(reeb['nodes'])))
        G.add_edges_from(reeb['edges'])
        num_components.append(len(list(nx.connected_components(G))))
    plt.plot(num_components)
    plt.xlabel('Timestep')
    plt.ylabel('#Connected components')
    plt.show()

def distance(n1, n2):
    return sqrt((n1[0] - n2[0]) ** 2 + (n1[1] - n2[1]) ** 2)


def plot_timestep(timestep, threshold=0):
    reeb_graph = timesteps[timestep]
    nodes = reeb_graph['nodes']
    edges = reeb_graph['edges']
    types = reeb_graph['types']
    lines = []
    filtered = []
    for edge in edges:
        if threshold > 0 and (
                (types[edge[0]] == 0 and types[edge[1]] == 3) or (types[edge[0]] == 3 and types[edge[1]] == 0)):
            if distance(nodes[edge[0]], nodes[edge[1]]) < threshold:
                filtered.append(edge[0])
                filtered.append(edge[1])
                continue
        lines.append([nodes[edge[0]], nodes[edge[1]]])
    lc = mc.LineCollection(lines, linewidths=1, color='black')
    fig, ax = plt.subplots()
    ax.add_collection(lc)
    ax.autoscale()
    ax.margins(0.01)
    ax.set_aspect(1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    x = [nodes[i][0] for i in range(len(nodes)) if i not in filtered]
    y = [nodes[i][1] for i in range(len(nodes)) if i not in filtered]
    colors = ['blue', 'green', 'yellow', 'red', 'gray']
    c = [colors[types[i]] for i in range(len(types)) if i not in filtered]
    ax.scatter(x, y, s=2.5, c=c)
    plt.show()
    return [x, y, c]


def analyze(timestep, threshold=0):
    reeb_graph = timesteps[timestep]
    nodes = reeb_graph['nodes']
    edges = reeb_graph['edges']
    types = reeb_graph['types']
    filtered = []
    for edge in edges:
        if threshold > 0 and (
                (types[edge[0]] == 0 and types[edge[1]] == 3) or (types[edge[0]] == 3 and types[edge[1]] == 0)):
            if distance(nodes[edge[0]], nodes[edge[1]]) < threshold:
                filtered.append(edge[0])
                filtered.append(edge[1])
                continue
    x = [nodes[i][0] for i in range(len(nodes)) if i not in filtered]
    y = [nodes[i][1] for i in range(len(nodes)) if i not in filtered]
    colors = ['blue', 'green', 'yellow', 'red', 'gray']
    filtered_type = [types[i] for i in range(len(types)) if i not in filtered]
    # print(filtered_type.count(0))
    # print(filtered_type.count(3))
    return [filtered_type.count(0), filtered_type.count(3)]


def count_critical():
    plot_timestep(300, threshold=40)
    plot_timestep(550, threshold=40)
    # print(len(timesteps));
    data = []
    for i in range(len(timesteps)):
        data.append(analyze(i, 0))
    a = np.array(data)
    # print(a)
    plt.plot(a[:, 0], c='blue')
    plt.plot(a[:, 1], c='red')
    plt.xlabel("Frame")
    plt.ylabel("#Critical Points")
    plt.show()

count_parallel_channels()