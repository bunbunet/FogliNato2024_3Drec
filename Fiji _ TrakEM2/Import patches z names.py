# Albert Cardona 2011-06-05
# Script for Colenso Speer
# Modified in order to scale images according to their pixel size and 
# to be used multiple times on the same folder without re-importing previously imported images
 
import os, re
from ini.trakem2 import Project
from ini.trakem2.display import Display, AreaList
from ini.trakem2.display import Patch
from java.awt.geom import AffineTransform
from ij import IJ
from ij.plugin import Duplicator
 

folder = " /path/to/folder/with/all/images/ "
# 1. Create a TrakEM2 project
# project = Project.newFSProject("blank", None, folder)

# OR: get the first open project
project = Project.getProjects().get(0)
 
layerset = project.getRootLayerSet()
 
#  2. Create 10 layers (or as many as you need)
for i in range(300):
  layerset.getLayer(i, 1, True)
 
# ... and update the LayerTree:
project.getLayerTree().updateList(layerset)
# ... and the display slider
Display.updateLayerScroller(layerset)

# Create a List of already existing patches
nameList = []
for layer in Display.getFront().getLayerSet().getLayers():
	patches = layer.getDisplayables(Patch)
	for patch in patches:
		name = patch.title
		nameList.append(name)

#print(nameList)
 
# 3. To each layer, add images that have "_zN_" in the name
#     where N is the index of the layer
#     and also end with ".tif"
filenames = os.listdir(folder)
for i,layer in enumerate(layerset.getLayers()):
  # EDIT the following pattern to match the filename of the images
  # that must be inserted into section at index i:
  pattern = re.compile(".*_z" + str(i) + "_.*\.tif")
  for filename in filter(pattern.match, filenames):
    if not filename in nameList:
    	filepath = os.path.join(folder, filename)
    	patch = Patch.createPatch(project, filepath)
    	layer.add(patch)
# resize the patches according to the pixel size of the images, setting a 1um per pixel project   	
    	imp = patch.getImagePlus()
    	calibration = imp.getCalibration()
    	pSize = calibration.pixelWidth
    	aff = AffineTransform()
    	CurrentScale = patch.getAffineTransform().getScaleX()
    	aff.scale(pSize/CurrentScale, pSize/CurrentScale)
    	patch.preTransform(aff, True)
    	patch.updateBucket()

  # Update internal quadtree of the layer
  layer.recreateBuckets()

# 4. Montage each layer independently

 
# 5. Resize width and height of the world to fit the montages
layerset.setMinimumDimensions()
 
# 6. Blend images of each layer
#Blending.blendLayerWise(layerset.getLayers(), True, None)

# 7. Save the project
#project.saveAs(os.path.join(folder, Specimen +".xml"), False)
 
print "Done!"