# TIFF loading stuff
import tifffile

# Visualization stuff
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.animation as animation

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

display_animation()