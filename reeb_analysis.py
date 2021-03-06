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
from matplotlib.gridspec import GridSpec

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
        elif len(list(filter(lambda n: nodes[n][0] < node[0], adjacent_nodes))) > 1:
            types[id] = 2
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

def calculate_betti():
    b0 = []
    b1 = []
    for reeb in timesteps:
        G = nx.Graph()
        G.add_nodes_from(range(len(reeb['nodes'])))
        G.add_edges_from(reeb['edges'])
        b0.append(len(list(nx.connected_components(G))))
        b1.append(len(list(nx.cycle_basis(G))))
    plt.plot(b0)
    plt.xlabel('Timestep')
    plt.ylabel('0th Betti number')
    plt.show()
    plt.plot(b1)
    plt.xlabel('Timestep')
    plt.ylabel('1st Betti number')
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
    # plt.show()
    return [x, y, c, lines]


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
    return [filtered_type.count(0), filtered_type.count(1), filtered_type.count(2), filtered_type.count(3)]


def count_critical():
    data = []
    for i in range(len(timesteps)):
        counts = analyze(i, 0)
        counts.append(sum(counts))  # sum all counts
        data.append(counts)
    a = np.array(data)
    plt.plot(a[:, 0], c='blue', label="minima")
    plt.plot(a[:, 1], c='y', label="split")
    plt.plot(a[:, 2], c='g', label="merge")
    plt.plot(a[:, 3], c='red', label="maxima")
    plt.plot(a[:, 4], c='black', label="total")
    plt.xlabel("Frame")
    plt.ylabel("Number of Critical Points")
    plt.title("Number of critical points over time")
    plt.legend()
    plt.show()


def plot_nr_edges(thresholds : list[int]):
    for threshold in thresholds:
        nr_edges = []
        for timestep in timesteps:
            edges = timestep['edges']
            nodes = timestep['nodes']
            edge_count = 0
            for edge in edges:
                if distance(nodes[edge[0]], nodes[edge[1]]) >= threshold:
                    edge_count += 1
            nr_edges.append(edge_count)

        plt.plot(nr_edges, label=f"Number of edges with length at least {threshold}")
    plt.legend()
    plt.xlabel("Frame")
    plt.ylabel("Number of edges")
    plt.title(f"Number of edges of set threshold over time")
    plt.show()

def show_reebgraph_steps():
    fig = plt.figure()
    gs = GridSpec(6,1)

    for i,x in enumerate([0, 132, 264, 396, 528, 661]):
        ax = fig.add_subplot(gs[i,0])
        ax.tick_params(labelbottom=False)
        ax.axis('off')
        ax.tick_params(labelleft=False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        data = plot_timestep(x, 40)
        ax.scatter(x=data[0], y=data[1], s=2.5, c=data[2])
        lc = mc.LineCollection(data[3], linewidths=1, color='black')
        ax.add_collection(lc)

    plt.show()

def plot_edge_lengths(threshold=0):
    means = []
    medians = []
    q1s = []
    q3s = []
    # Compute mean, median and 25th and 75th percentile per frame
    for timestep in timesteps:
        edges = timestep['edges']
        nodes = timestep['nodes']
        lengths = []
        for edge in edges:
            n1 = nodes[edge[0]]
            n2 = nodes[edge[1]]
            if distance(n1, n2) >= threshold:
                lengths.append(distance(n1, n2))

        means.append(np.mean(lengths))
        medians.append(np.median(lengths))
        q1s.append(np.percentile(lengths, 25))
        q3s.append(np.percentile(lengths, 75))

    plt.plot(means, label="mean", c="red")
    #plt.plot(medians, label="median")
    plt.plot(q1s, label="25th percentile", c="lightcoral")
    plt.plot(q3s, label="75th percentile", c="darkred")
    plt.legend()
    plt.xlabel("Frame")
    plt.ylabel("Edge length")
    if threshold == 0:
        plt.title('Edge length statistics over time')
    else:
        plt.title(f'Edge length statistics with threshold {threshold} over time')
    plt.show()

def plot_total_edges_nodes():
    nodes = []
    edges = []
    for timestep in timesteps:
        nodes.append(len(timestep['nodes']))
        edges.append(len(timestep['edges']))
    plt.plot(nodes, label="Number of nodes")
    plt.plot(edges, label="Number of edges")
    plt.title(f'Total number of nodes and edges over time')
    plt.legend()
    plt.xlabel("Frame")
    plt.show()

# all nodes with x-coord less that source_threshold are connected to a source, vice versa for sink
# gap threshold connects maxima with minima if their distance is less than gap_threshold
def compute_max_flow(source_threshold, sink_threshold, gap_threshold=0):
    flows = []
    for reeb in timesteps:
        G = nx.Graph()
        G.add_nodes_from(range(len(reeb['nodes'])))
        G.add_edges_from(reeb['edges'])
        # Connect gaps
        if gap_threshold > 0:
            for n1 in range(len(reeb['nodes'])):
                if reeb['types'][n1] != 3: continue
                for n2 in range(len(reeb['nodes'])):
                    if reeb['types'][n2] != 1: continue
                    if n1 == n2: continue
                    if reeb['nodes'][n1][0] > reeb['nodes'][n2][0]: continue
                    if distance(reeb['nodes'][n1], reeb['nodes'][n2]) <= gap_threshold:
                        if not (G.has_edge(n1, n2) or G.has_edge(n2, n1)):
                            G.add_edge(n1, n2)
        # Add & connect source s and sink t
        G.add_node('s')
        G.add_node('t')
        for n in range(len(reeb['nodes'])):
            node = reeb['nodes'][n]
            if (node[0] <= source_threshold): G.add_edge('s', n)
            if (node[0] >= sink_threshold): G.add_edge(n, 't')
        nx.set_edge_attributes(G, 1, 'capacity')
        flows.append(nx.maximum_flow_value(G, 's', 't'))
    plt.plot(flows)
    plt.xlabel('Timestep')
    plt.ylabel('Maximum flow value')
    plt.show()

#plot_timestep(250)
# plot_total_edges_nodes()
# plot_edge_lengths()
#plot_edge_lengths(5)
# plot_nr_edges([0, 5, 10, 15])
# count_critical()
# show_reebgraph_steps()
# calculate_betti()
compute_max_flow(400, 1200, gap_threshold=100)