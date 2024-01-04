'''
This script add a sphere (25um diameter by default) at coordinates from text file organized as:             Specimen,ID,CellType,pz,Region,Subregion,SubSubregion,Marker,notes,FullName,x,y,z,radius (file with header)
or as
Specimen,ID,Name,x,y,z,radius (file with no header)

These files where exported from TraKEM2, the z and y coordinates are swapped. 
(TO DO: To correspond to the original brains, they would also need to be rotated 180° and mirrored on the y axis)
It require to specify the path to the trace file name
It than color and group the cells according to the cell type (PreS, STARTER, Retro) and location (region)
Groups are made from the txt file and is applyed only to imported objects

CAREFUL!! !Grouping do not take in to the account the position of the acronym in the file name
it work properly only if each acronym or name is unique!
'''

import os
import bpy

#------------------------------------USER DEFINED OPTIONS---------------------------

#Define the reference object for transformation (specimen name will be automatically identified)
#e.g "An_LV" "An_STR"
#TO IMPORT WITHOUT TRANSFORMATIONS LEAVE EMPTY
reference_object ="An_STRdx-Les"

#specify the path to file name (add double \\ to escape special charachters. eg if the folder is called txt use \\txt)
WORKING_DIR = "C:\\Users\\feder\\Documents\\LAB\\ProgettoQA\\Dynamic\\5w 3D reconstruction\\Balls"
file_name = "CONFd1620.1_clusters.txt"
file_path = os.path.join(WORKING_DIR, file_name)
#file_path ="G:\\Progetto QA\\RR\\Export Results\\txt\\RR10_mapped.txt"

# Set balls_type="mesh" to import balls as mesh; set balls_type="surface" to import balls as nurbs.
# Nurbs require less memory but transparency is not rendered in object mode.
balls_type="surface"

#Set True to organize the balls in groups according to specimen, region and cell Type
group_balls=False

# SET THE BALL SIZE (In micron, consider also possible additional scale factors in the TrakEM2 project)
# WHEN APPLYING THE TRANSFORMATION THE SPECIFIED VALUE WILL BE SCALED ACCORDING TO THE REFERENCE OBJECT 
# VERIFY IT IN ORDER TO HAVE THE desired value in micron!!
# FOR TrakEM2 0,756 scale Ball size=33.08 is 25 microns
# FOR TrakEM2 1,517 scale Ball size=16.48 is 25 microns
BallSize=25

#Set true to to color cortical cells by subregion (see matPreS_subregion_list)
Color_Subregions = True

matType_list = ["PreS", "Retro", "STARTER"]
matPreS_region_list = ["SVZ","STR","TH","_CX"]
matPreS_subregion_list = ["ACA", "AI", "AUD", "ENTl","FRP","MOp","MOs","ORB","PIR","PL","PTL","RSP","SS","VIS","ILA"]

# Set the scale factor (if applying the transformation of pre-existing object, the scale is automatically set to set=1)
sf = 0.001
if len(reference_object)>0:
    sf=1

#----------------------------------------READ THE FILE AND CREATE CLASSIFICATION SETS---------------------

#lines = [line.strip() for line in open(file_path, "r").readlines()]
linesTXT = [line.strip() for line in open(file_path, "r").readlines()]

#select only the lines with the proper code (12 parameters, for brain mapped cells or 7 for unmapped cells) 
# skipped lines are printed in the console
# A variable type is set to more shortly define later in the script if mapped or unmapped cells are imported
lines=[]
lines_unmapped=[]
for line in linesTXT:  
    if len(line.split(","))>=12:
        type="Mapped"
        lines.append(line)
    elif len(line.split(","))==8:
        type="Unmapped"
        lines_unmapped.append(line)
    else:
        print("not imported:",line)

#Create the callisification sets (lists with no duplicates) from the imported txt file:
#animals, cell type, regions, subregions, subsubregions
#an underscore precede the region name to cluster balls groups in the outliner.
#This also make the sets more univoques, simplifying the grouping step
    
# animals
if type=="Mapped":
    animals= set([line.split(",")[0] for line in lines[1:]])
    print("animals", animals)

if type=="Unmapped":
    animals= set([line.split(",")[0] for line in lines_unmapped[1:]])
    print("animals", animals)
    
# cell types
if type=="Mapped":
    cells_set= set(["_"+line.split(",")[2] for line in lines[1:]])
    print("cells types", cells_set)
#additional cell types such as STARTER-nbl and STARTER-glial could be added, use .add for single item
#cell_set.update([STARTER-nbl,STARTER-glial])

# region
if type=="Mapped":
    regions = set(["_"+line.split(",")[4] for line in lines[1:]])
    print("regions", regions)

# subregion
if type=="Mapped":
    subregions = set(["_"+line.split(",")[4] + "_" + line.split(",")[5] for line in lines[1:] if  line.split(",")[5] != " "])
    #subregions.remove(" ")
    print("subregions",subregions)

# subsubregion
if type=="Mapped":
    subsubregions = set(["_"+line.split(",")[4] + "_" + line.split(",")[5] + "_" + line.split(",")[6] for line in lines[1:] if line.split(",")[5] != " " and line.split(",")[6] != " "])
    #subregions.remove(" ")
    print("subsubregions", subsubregions)

#--------------------------------GET THE TRANSFORMATION MATRIX OF REFERENCE OBJECT-----------

bpy.ops.object.select_all(action='DESELECT')

if len(reference_object)==0:
    print("no reference surface selected") 

#Searching for an object with the same animal prefix as the imported balls and select it
nameRef=list(animals)[0]+"_"+ reference_object
for ob in bpy.data.objects:
    if ob.name.find(nameRef) !=-1:
        ob.select = True
        bpy.context.scene.objects.active = ob
        print("Reference object:",ob.name)

#set the cursor to the origin
bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)  
#get the transforma matrix of the selected object
M=bpy.context.object.matrix_world
#store the position of object's origin
loc=bpy.context.object.location
#bpy.context.scene.cursor_location = loc
print(M)
print(loc)

#-----------------------------------------IMPORT BALLS-----------------------------------------
print("Importing mapped cells")
#create a list for the name of imported objects
objects_to_add =[]

#create spheres, the original Y and Z are swapped and Y (now Z) mirrored
for e in lines[1:]:
    temp = e.split(',')
    if len(temp)>=12:
        #the x,y,z, order is different wheter the balls are simply imported or transformed on pre-existing surface
        if len(reference_object)==0:
            a=float(temp[10])*sf
            b=float(temp[12])*sf
            c=float(temp[11])*-sf
        else:
            a=float(temp[10])*sf
            b=float(temp[11])*sf
            c=float(temp[12])*sf
        if balls_type=="mesh":
            bpy.ops.mesh.primitive_uv_sphere_add(segments = 12, ring_count = 12, location=(a,b,c),size = BallSize*sf)
        
        elif balls_type=="surface":
        #Nurbs Spheres (comment out the me.update if importing surfaces)
            bpy.ops.surface.primitive_nurbs_surface_sphere_add(radius=BallSize*sf, view_align=False, enter_editmode=False, location=(a,b,c))
        
        bpy.ops.object.shade_smooth()
        bpy.context.object.name = str(temp[0]+"_"+temp[9])
        obj_object = bpy.context.selected_objects[0]
        objects_to_add.append(obj_object)
        #set the origin of the sphere to 0,0,0.
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        #If a reference object is specified, apply the transformation matrix to the imported balls.
        if len(reference_object)>0:
            ob = bpy.context.object
            me = ob.data
            me.transform(M)      
            if balls_type=="mesh":
                me.update()
        
        #bpy.ops.transform.rotate(value=1.5708, axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='ENABLED', proportional_edit_falloff='SMOOTH', proportional_size=2.59374)
        #Set the origin of the ball to its center
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')        
    else:
        print("not imported ball:\n", temp)

print("Imported objects: ",len(objects_to_add))

#--------------------------------------------------------IMPORT UNMAPPED BALLS----------------------------
print("unmapped cells")
#Create a Ball at the location of each ref point 
for e in lines_unmapped[1:]:   
    temp = e.split(',')
        #the x,y,z, order is different wheter the balls are simply imported or transformed on pre-existing surface
    if len(reference_object)==0:       
        a=float(temp[4])*sf
        b=float(temp[6])*sf
        c=float(temp[5])*-sf
    else:
        a=float(temp[4])*sf
        b=float(temp[5])*sf
        c=float(temp[6])*sf
    if balls_type=="mesh":
        bpy.ops.mesh.primitive_uv_sphere_add(segments = 12, ring_count = 12, location=(a,b,c),size = BallSize*sf)
        
    elif balls_type=="surface":
        #Nurbs Spheres (comment out the me.update if importing surfaces)
        bpy.ops.surface.primitive_nurbs_surface_sphere_add(radius=BallSize*sf, view_align=False, enter_editmode=False, location=(a,b,c))
        
    bpy.ops.object.shade_smooth()
    bpy.context.object.name = str(temp[0]+"_"+temp[2]+"_"+temp[3])
    obj_object = bpy.context.selected_objects[0]
    objects_to_add.append(obj_object)
    #set the origin of the sphere to 0,0,0.
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    #If a reference object is specified, apply the transformation matrix to the imported balls.
    if len(reference_object)>0:
        ob = bpy.context.object
        me = ob.data
        me.transform(M)      
        if balls_type=="mesh":
            me.update()
    #Set the origin of the ball to its center        
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')  
  
#-----------------------------------------------------------COLOR CELLS--------------------------------------
print("color imported cells")
#to simplify copy-paste of pre-existing code for material assignement.. 
objects=objects_to_add

#Color by Cell Type
matType_dict = {}
for material in matType_list:
    matType_dict[material] = bpy.data.materials.get(material)
    
for ob in objects:
    if len(ob.name.split("_"))>6 and ob.type=="SURFACE" or ob.type=="MESH":
        ob_split=ob.name.split("_")
        for material in matType_dict:
            if ob_split[1].find(material) != -1:
                if ob.data.materials:
                    ob.data.materials[0] = matType_dict[material]
                else:
                    ob.data.materials.append(matType_dict[material])

                        
#---------------------------------------------GROUP MAPPED CELLS----------------------------------
print("Grouping cells")
object_names = [obj.name for obj in objects]
scn = bpy.context.scene

if group_balls:
    #create groups for each set
    for animal in animals:
        if not animal in bpy.data.groups:
            bpy.ops.group.create(name=animal)
            
if type=="Mapped" and group_balls:
    for cell_type in cells_set:
        if not cell_type in bpy.data.groups:
            bpy.ops.group.create(name=cell_type)
            print(cell_type)

    for region in regions:
        if not region in bpy.data.groups:
            bpy.ops.group.create(name=region)

    #link imported balls to their corresponding group !(work only if each acronym or name is unique!)
if type=="Mapped":
    for name in object_names:
        for cell_type in list(animals) + list(cells_set) + list(regions):
            if name.find(cell_type) != -1:
                scn.objects.active = scn.objects[name]
                bpy.ops.object.group_link(group=cell_type)
elif type=="Unmapped":
    for name in object_names:
        for cell_type in list(animals):
            if name.find(cell_type) != -1:
                scn.objects.active = scn.objects[name]
                bpy.ops.object.group_link(group=cell_type)
