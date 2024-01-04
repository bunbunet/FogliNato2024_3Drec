

from ini.trakem2.display import Display, Ball
from ij.text import TextWindow
from ini.trakem2 import Project
import os

#export id, title and coordinates of balls in balls objects,
#split names according to the convention : Type_pz_region_subregion_sub-subregion_label_notes
# BE CAREFUL! ONLY ONE PROJECT SHOULD BE OPEN, otherwise specimen names could not correspond
#to the display balls exported


Output_DIR_mapped="G:\\Progetto QA\\RR\\Export Results\\Neurons_Rec_obj\\" # MUST have ending slash
Output_DIR_REF="G:\\Progetto QA\\RR\\Export Results\\Neurons_Rec_obj\\" # MUST have ending slash
Output_DIR_unmapped="G:\\Progetto QA\\RR\\Export Results\\Neurons_Rec_obj\\" # MUST have ending slash

#Setting true text windows with the results are directly opened in ImageJ
open_text_window=False

#set as "" to process only already opened projects
#set a path to open all the .xml file in a folder

batch_folder=""

if len(batch_folder)>0:
	filenames = os.listdir(folder)
	for name in filenames:
		if ".xml" in name:
			#open project without display
			project = Project.openFSProject(batch_folder + name, False)
			specimen= str(name).split(".xml")[0]
			print(specimen)

projects=Project.getProjects()
for project in projects:
	specimen= str(project).split(".xml")[0]
	ball_obs = project.getRootLayerSet().getZDisplayables(Ball)
	print(specimen, len(ball_obs))
	# One entry for each id,x,y,z,r 
	
	#List for mapped balls
	rows_Mapped = []
	rows_Unmapped= []
	rows_REF= []

	#Create the files and open it
 	Mapped_txt_path = os.path.join(Output_DIR_mapped, specimen+"_"+"mapped"+".txt")
 	Unmapped_txt_path = os.path.join(Output_DIR_unmapped, specimen+"_"+"unmapped"+".txt")
 	REF_txt_path = os.path.join(Output_DIR_REF, specimen+"_"+"REF"+".txt") 
	# Iterate every Ball instance, which contains one or more x,y,z,r balls
	for ball_ob in ball_obs:
		id = ball_ob.getId()
	 	title = ball_ob.getTitle()
		g=title.split("_")
		# Iterate every x,y,z,r ball of a Ball instance, calibrated
		wbs = ball_ob.getWorldBalls()
		for ball_coords in wbs:
	    # Store every ball as a row with id, x, y, z, r; for brain mapped balls the name is parsed into separated columns 
	    # this is not necessary, but facilitate analysis in softwares where parsing the names is not as straightforward as in python (i.e Excel, SPSS, R etc..)
				if len(g)>6: #Balls 
					rows_Mapped.append(str(specimen)+","+str(id)+","+g[0]+","+g[1]+","+g[2]+","+g[3]+","+g[4]+","+g[5]+","+g[6]+","+title+","+",".join(str(c) for c in ball_coords))
				elif "REF" in title: 
					rows_REF.append(str(specimen)+","+str(id)+","+title+","+",".join(str(c) for c in ball_coords))
				else:
					rows_Unmapped.append(str(specimen)+","+str(id)+","+title+","+",".join(str(c) for c in ball_coords))
	
	#here the header for the mapped file
	rows_Mapped.insert(0,str("Specimen")+","+str("ID")+","+str("CellType")+","+str("pz")+","+str("Region")+","+str("Subregion")+","+str("SubSubregion")+","+str("Marker")+","+str("notes")+","+str("FullName")+","+str("x")+","+str("y")+","+str("z")+","+str("radius"))

	print("Mapped balls:",len(rows_Mapped))
	print("Unmapped balls:",len(rows_Unmapped))
	print("REF balls:",len(rows_REF))

	# QUesto scrive ma non mi salta le righe, o
	with open(Mapped_txt_path, 'wb') as f:
		f.write("\n".join(rows_Mapped))
	
	with open(Unmapped_txt_path, 'wb') as f:
		f.write("\n".join(rows_Unmapped))

	with open(REF_txt_path, 'wb') as f:
		f.write("\n".join(rows_REF))
	
	if open_text_window:
		csv = "\n".join(rows_Mapped)
		csv2 = "\n".join(rows_Unmapped)
		csv3 = "\n".join(rows_REF)
		t = TextWindow(specimen+"_balls", csv, 400, 400)
		t2 = TextWindow(specimen+"_unmapped", csv2, 400, 400)
		t3 = TextWindow(specimen+"_REF", csv3, 400, 400)
