import tifffile
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# Paths to data, baseline and detrended stack
BASELINE_PATH = "data/baseline.tiff"
DETRENDED_PATH = "data/detrended/detrended_xxxx.tif"

# Load baseline data
baseline_data = tifffile.imread(BASELINE_PATH)
print("Baseline shape: " + str(baseline_data.shape))
# Load detrended data stack
detrended_data = []
for i in range(1,663):
    detrended_data.append(tifffile.imread(DETRENDED_PATH.replace("xxxx", str(i).zfill(4))))
detrended_data = np.array(detrended_data)
print("Detrended shape: " + str(detrended_data.shape))

# Add baseline to detrended to make height field
heights = []
for i in range(len(detrended_data)):
    heights.append(np.add(baseline_data, detrended_data[i]))
heights = np.array(heights)

def visualize_mask(mask):
    plt.imshow(mask, cmap='RdYlBu_r')
    plt.show()

def tuple_intersects(t1, t2):
    if t1[0] > t2[0]: return tuple_intersects(t2, t1)
    if t1[1] < t2[0]: return False
    return True

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.neighbors = []

def reeb(data, threshold):
    mask = data < threshold
    mask = np.transpose(mask)
    # Find contours
    contours = [[] for y in range(len(mask))]
    for y in range(len(mask)):
        tracking = False
        tracking_start = -1
        for x in range(len(mask[y])):
            if mask[y][x] and not tracking:
                tracking = True
                tracking_start = x
            elif not mask[y][x] and tracking:
                tracking = False
                contours[y].append((tracking_start, x-1))
                tracking_start = -1

    # trace reeb graph
    nodes = [[None for x in range(len(mask[0]))] for y in range(len(mask))]

    
    return contours

# visualize_mask(reeb(heights[550], 25000000))
reeb(heights[550], 25000000)