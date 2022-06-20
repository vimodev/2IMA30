from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import matplotlib.collections as mc

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
for reeb_graph in timesteps:
    nodes = reeb_graph['nodes']
    edges = reeb_graph['edges']
    reeb_graph['types'] = [4 for i in range(len(nodes))]
    types = reeb_graph['types']
    for id in range(len(nodes)):
        node = nodes[id]
        adjacent_edges = list(filter(lambda edge: edge[0] == id or edge[1] == id, edges))
        adjacent_nodes = []
        for edge in adjacent_edges:
            if edge[0] != id: adjacent_nodes.append(edge[0])
            elif edge[1] != id: adjacent_nodes.append(edge[1])
        # Check minimum type
        if node[0] <= min([nodes[n][0] for n in adjacent_nodes]): types[id] = 0
        # Check maximum type
        elif node[0] >= max([nodes[n][0] for n in adjacent_nodes]): types[id] = 3
        # Check split node
        elif len(list(filter(lambda n: nodes[n][0] > node[0], adjacent_nodes))) > 1: types[id] = 1
        # Check merge node
        elif len(list(filter(lambda n: nodes[n][0] < node[0], adjacent_nodes))) > 1: types[id] = 2

print("Data preparation done!")

def plot_timestep(timestep):
    reeb_graph = timesteps[timestep]
    nodes = reeb_graph['nodes']
    edges = reeb_graph['edges']
    types = reeb_graph['types']
    lines = []
    for edge in edges:
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
    x = [node[0] for node in nodes]
    y = [node[1] for node in nodes]
    colors = ['blue', 'green', 'yellow', 'red', 'gray']
    ax.scatter(x, y, s=2.5, c=[colors[ntype] for ntype in types])
    plt.show()

# print(timesteps[660]['types'])
plot_timestep(660)
