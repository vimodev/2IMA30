import tifffile

BASELINE_PATH = "../data/baseline.tiff"
DETRENDED_PATH = "../data/detrended.tiff"

baseline_data = tifffile.imread(BASELINE_PATH)
print("Baseline shape: " + str(baseline_data.shape))
detrended_data = tifffile.imread(DETRENDED_PATH)
print("Detrended shape: " + str(detrended_data.shape))