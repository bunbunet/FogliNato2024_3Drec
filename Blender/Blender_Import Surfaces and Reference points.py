#Import of .obj files containing the anatomical structures exported from TraKEM2
#Name format of reference points: REF_CCant, REF_CCpost, REF_CA
#Name format of the surfaces: "Specimen_An_Region" e.g. RRGEF1_An_STRdx-Les
#All new objects will be added to the group "An_specimen Name"
#Anatomical structures will be automatically assigned with a material if their name is preceded by "An_" and contains the following expressions:
#BrainFast (Brain Surface) ; STR (striatum); Les (Lesioned tissue); WM: (white matter); LV (for ventricle); InjVir (Viral Injection); InjQA (QA injection).

import bpy
import glob

#------------------------------------USER DEFINED OPTIONS------------------------
#specify the path to file name
WORKING_DIR = "C:\\Users\\feder\\Documents\\LAB\\ProgettoQA\\Dynamic\\5w 3D reconstruction\\OBJ\\Import\\"

#Set the scale factor and the size of REF balls
sf=0.001
BallSize=25

#Set False if you don't want color the objects
Assign_material=True
# List of the existing materials that will be asigned based on correspondence with imported object names
matType_list = ["An_BrainFast","An_LV", "An_STR","An_Les", "An_BrainSlice","An_InjVir","An_InjQA","An_WM-pi"]

#---------------------------------CREATE THE PATH OF THE OBJECTS TO IMPORT-------------

#List all .obj files in the folder
obj_list=glob.glob(WORKING_DIR+"/*.obj")
#List of all txt files in the folder
Ref_list=glob.glob(WORKING_DIR+"/*.txt")

#--------------------------------------------------IMPORT OBJ---------------------------

#create list of already imported objects
Project_objects = (ob.name for ob in bpy.data.objects)

scn = bpy.context.scene
added_objects=[]
#import and remesh all .obj files    
for obj in obj_list:
    #extract the name of the object to import
    Name_of_obj=obj.replace(WORKING_DIR+"\\","")
    #Import only if the object is not already present in the porject
    if Name_of_obj.split(".obj")[0] not in Project_objects:
        #While importing we convert the axes so that the Z become Y and the Y is inverted 
        imported_object = bpy.ops.import_scene.obj(filepath=obj,axis_forward='Z', axis_up='-Y')
        obj_object = bpy.context.selected_objects[0] 
        added_objects.append(obj_object)
        #Scale the object (an alternative to conver the axes would be: value=(-sf,sf,-sf))
        obj_object.scale=(sf,sf,sf)
        
        #Remesh
        remesh = obj_object.modifiers.new(name="Remesh", type='REMESH')
        remesh.octree_depth = 7
        remesh.use_smooth_shade = True
        remesh.mode = 'SMOOTH'
        remesh.use_remove_disconnected = False
        remesh.scale = 0.5
        
        #Show transparency
        show_transparent = True
        
        #Group objects in a single Group per specimen
        specimen=("An_"+obj_object.name.split("_")[0])
        Region=(obj_object.name.split("_")[2])
        Region_Group="_An_"+Region
        if not specimen in bpy.data.groups:
            bpy.ops.group.create(name=specimen)
        scn.objects.active = scn.objects[obj_object.name]
        bpy.ops.object.group_link(group=specimen)
        if not Region_Group in bpy.data.groups:
            bpy.ops.group.create(name=Region_Group)
        scn.objects.active = scn.objects[obj_object.name]
        bpy.ops.object.group_link(group=Region_Group)
        print('Imported name: ', obj_object.name)
    else:
        print(Name_of_obj, " is already in the Project")

#-----------------------------------IMPORT REF and create Reference Plane----------------------------

#Create a Ball at the location of each ref point 
for obj in Ref_list:
    #split the lines
    lines = [line.strip() for line in open(obj, "r").readlines()]    
    objects_to_add =[]
    #split each line to obtain specimen name, ball name and coordinates
    for line in lines:           
        temp = line.split(',')
        #create the balls
        bpy.ops.mesh.primitive_uv_sphere_add(segments = 12, ring_count = 12,location=(float(temp[3])*sf,float(temp[5])*sf,float(temp[4])*-sf),size = BallSize*sf)
        bpy.ops.object.shade_smooth()
        bpy.context.object.name = str(temp[0]+"_"+temp[2])
        objects_to_add.append(bpy.context.object.name)
        #set the origin of the sphere to 0,0,0.
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        specimen=("An_"+temp[0])
        if not specimen in bpy.data.groups:
            bpy.ops.group.create(name=specimen)
        #scn.objects.active = scn.objects[obj_object.name]
        bpy.ops.object.group_link(group=specimen)
                  
#Create a triangle mesh that crosses CCant, CCpost and CA, only animals with all 3 ref points will be used   
for obj in Ref_list:
    lines = [line.strip() for line in open(obj, "r").readlines()]
    objects_to_add =[]
    if len(lines)>2:
        for line in lines:
            temp = line.split(',')
            if temp[2] =="REF_CCant":
                vertAnt=(float(temp[3])*sf,float(temp[5])*sf,float(temp[4])*-sf)  
            elif temp[2] =="REF_CCpost":
                vertPost=(float(temp[3])*sf,float(temp[5])*sf,float(temp[4])*-sf)           
            elif temp[2]=="REF_CA":
                vertCA=(float(temp[3])*sf,float(temp[5])*sf,float(temp[4])*-sf)      
                
        vertsData=[(vertAnt[0],vertAnt[1],vertAnt[2]),(vertPost[0],vertPost[1],vertPost[2]),(vertCA[0],vertCA[1],vertCA[2])]
        facesData=[(0,1,2)]
        # create new mesh structure
        mesh = bpy.data.meshes.new(temp[0]+"_REF-plane")
        mesh.from_pydata(vertsData, [], facesData)  
        mesh.update()

        new_object = bpy.data.objects.new(temp[0]+"_REF-plane", mesh)
        new_object.data = mesh

        scene = bpy.context.scene
        scene.objects.link(new_object)
        scene.objects.active = new_object
        new_object.select = True
        specimen=("An_"+temp[0])
        if not specimen in bpy.data.groups:
            bpy.ops.group.create(name=specimen)
        bpy.ops.object.group_link(group=specimen)     

#--------------------------------------------------COLOR OBJECTS--------------------------------------

if Assign_material: 
    #Create a dictionary in which existing materials are selected from
    matType_dict = {}
    for material in matType_list:
        matType_dict[material] = bpy.data.materials.get(material)

    #Color by Region    
    for ob in added_objects:
        if len(ob.name.split("_"))>2 and ob.type=="MESH":
            ob_split=ob.name.split("_")
            ob_region=ob_split[1]+"_"+ob_split[2]
            for material in matType_dict:
                if ob_region.find(material) != -1:  
                    if ob.data.materials:
                        ob.data.materials[0] = matType_dict[material]
                        ob.show_transparent = True
                        
    #Differentially Color Lesioned areas
    Les=bpy.data.materials.get("An_Les")
    for ob in added_objects:
        if ob.name.find("Les") !=-1:  
            ob.data.materials[0] = Les
            
