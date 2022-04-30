# TIFF loading stuff
import tifffile

# Visualization stuff
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.animation as animation

# General stuff
import numpy as np

# Paths to data, baseline and detrended stack
BASELINE_PATH = "../data/baseline.tiff"
DETRENDED_PATH = "../data/detrended.tiff"

# Load baseline data
baseline_data = tifffile.imread(BASELINE_PATH)
print("Baseline shape: " + str(baseline_data.shape))
# Load detrended data stack
detrended_data = tifffile.imread(DETRENDED_PATH)
print("Detrended shape: " + str(detrended_data.shape))

# Display an animated progression over time of the data
def display_animation():
    frames = []
    fig = plt.figure()
    # Generate frame for every page in the detrended_data stack
    for i in range(len(detrended_data)):
        frames.append([plt.imshow(detrended_data[i] + baseline_data, cmap='RdYlBu_r', animated=True)])
    ani = animation.ArtistAnimation(fig, frames, interval=16, blit=True,
                                    repeat_delay=1000)
    plt.show()

# Display graph showing rate of change over time
def display_rate_of_change(rolling_window=100):
    # Calculate delta in the data at every frame
    changes = []
    for i in range(len(detrended_data) - 1):
        changes.append(np.sum(np.absolute(detrended_data[i] - detrended_data[i + 1])))
    # Normalize
    changes = changes / np.max(changes)
    # Apply rolling average
    rolling = [sum(changes[i:i+rolling_window])/float(rolling_window) for i in range(len(changes)-rolling_window+1)]
    plt.title('Rate of change, rolling avg (window = ' + str(rolling_window) + ')')
    plt.ylabel('Change (normalized)')
    plt.xlabel('Frame')
    plt.plot(rolling)
    plt.show()

display_animation()
display_rate_of_change()