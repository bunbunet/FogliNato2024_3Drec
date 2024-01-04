from ini.trakem2.display import Display, Patch
from java.awt import Color

stains= ["RFP", "GFP", "Ki67", "DCX"]
# Set 1 for ADD, 0 for Normal, 4 for difference
mode=1


for layer in Display.getFront().getLayerSet().getLayers():
				patches = layer.getDisplayables(Patch)
				for patch in patches:
					for stain in stains:
						if stain in patch.title:
							# Set the transparency (alpha value)
							patch.alpha = 1
							patch.setCompositeMode(mode)
						
Display.repaint()