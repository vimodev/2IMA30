from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import matplotlib.collections as mc

# Fetch all the files
print("Enumerating files...")
OBJ_PATH = 'reeb_exports'
files = sorted([join(OBJ_PATH, f) for f in listdir(OBJ_PATH) if isfile(join(OBJ_PATH, f))])

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
print("Done parsing files...")

def plot_timestep(timestep):
    reeb_graph = timesteps[timestep]
    nodes = reeb_graph['nodes']
    edges = reeb_graph['edges']
    lines = []
    for edge in edges:
        lines.append([nodes[edge[0]], nodes[edge[1]]])
    lc = mc.LineCollection(lines, linewidths=1)
    fig, ax = plt.subplots()
    ax.add_collection(lc)
    ax.autoscale()
    ax.margins(0.01)
    ax.set_aspect(1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    plt.show()

plot_timestep(660)
