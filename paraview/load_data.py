from os import listdir
from os.path import join
from paraview.simple import *

# Viewport stuff
view = GetActiveViewOrCreate('RenderView')
view.ResetCamera(False)
view.update()

# What files?
detrended_directory = 'C:\\Users\\Vincent\\git\\2IMA30\\data\\detrended\\'
detrended_files = [join(detrended_directory, f) for f in listdir(detrended_directory)]
baseline_file = 'C:\\Users\\Vincent\\git\\2IMA30\\data\\baseline.tiff'

# Load the data
detrended = TIFFSeriesReader(registrationName='detrended', FileNames=detrended_files, ReadAsImageStack=False)
baseline = TIFFSeriesReader(registrationName='baseline', FileNames=baseline_file)

# Combine data into single object
combined = AppendAttributes(registrationName='combined', Input=[detrended, baseline])

# Add data in the object, and write to new data array
height = Calculator(registrationName='height', Input=combined)
height.Function = '"Tiff Scalars"+"Tiff Scalars_input_1"'
height.ResultArrayName = 'heights'

# Render the data
height_display = Show(height, view, 'UniformGridRepresentation')
height_display.Representation = 'Slice'
view.update()