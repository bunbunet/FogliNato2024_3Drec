// This Macro split stacks into separate channels, adding label names. It also produce a MAX projection the image sequence.
//Image sequence files are also attributed a z level (reading it from file aname) and print it to a .csv file that can be used
//to import these images in TrakEM2 using import from text file function. Each file type will be saved in a specific folder


dir=getDirectory("Choose source Directory");
print(dir);
splitDir= dir +"\\Split\\";
Zdir = dir+"\\MAX\\";
ch1 = getString("Name of Channel_1:", "GFP");
LUT1 = getString("LUT:","Green");
ch2 = getString("Name of Channel_2:", "Ki67");
LUT2 = getString("LUT:","Magenta");
ch3 = getString("Name of Channel_3:", "RFP");
LUT3 = getString("LUT:", "Red");
ch4 = getString("Name of Channel_4:", "DCX");
LUT4 = getString("LUT:", "Grays");
print(splitDir);
print(Zdir);
File.makeDirectory(splitDir);
File.makeDirectory(Zdir); 
list = getFileList(dir);

setBatchMode(true); 
for (i=0; i<list.length; i++) {
     if (endsWith(list[i], ".tif")){
               print(i + ": " + dir+list[i]);
             open(dir+list[i]);
             imgName=getTitle();
             print(imgName);
             getDimensions(width, height, channels, slices, frames);
             print(channels);
             
			 if (channels==1) {
			 run(LUT1);
         saveAs("Tiff", splitDir+ch1+"-"+imgName + ".tif");	
			 }
         	 else if (channels==4) {
	   run("Split Channels");
         selectWindow("C1-"+ imgName);
         run(LUT1);
         saveAs("Tiff", splitDir+ch1+"-"+imgName + ".tif");
         close();
         selectWindow("C2-"+ imgName);
         run(LUT2);
         saveAs("Tiff", splitDir+ch2+"-"+imgName + ".tif");
         close();
         selectWindow("C3-"+ imgName);
         run(LUT3);
         saveAs("Tiff", splitDir+ch3+"-"+imgName + ".tif");
         run("Grays");
         close();
         selectWindow("C4-"+ imgName);
         run(LUT4);
         saveAs("Tiff", splitDir+ch4+"-"+imgName + ".tif");
         close();
         }
			else if (channels==3){
	     run("Split Channels");
         selectWindow("C1-"+ imgName);
         run(LUT1);
         saveAs("Tiff", splitDir+ch1+"-"+imgName + ".tif");
         close();
         selectWindow("C2-"+ imgName);
         run(LUT2);
         saveAs("Tiff", splitDir+ch2+"-"+imgName + ".tif");
         close();
         selectWindow("C3-"+ imgName);
         run(LUT3);
         saveAs("Tiff", splitDir+ch3+"-"+imgName + ".tif");
         close();
         }
			else {
	     run("Split Channels");
         selectWindow("C1-"+ imgName);
         run(LUT1);
         saveAs("Tiff", splitDir+ch1+"-"+imgName + ".tif");
         close();
         selectWindow("C2-"+ imgName);
         run(LUT2);
         saveAs("Tiff", splitDir+ch2+"-"+imgName + ".tif");
         close();
}
         run("Close All");
     }
} 

// Create Two Arrays to store the name of single focal planes and their z position
// At the end of the macro these array are printed in a csv file that can be used to import these focal planes into TrakEM2
Fname=newArray
Zlayer=newArray

// This produce the image sequnece
//ACTIVATE/comment out THIS BLOCK TO SAVE (or not) ALSO THE IMAGE SEQUENCE OF EACH CHANNEL
dir2 = dir+"\\Sequence\\";
print(dir2);
File.makeDirectory(dir2);
list2 = getFileList(splitDir); 
	for (i=0; i<list2.length; i++) { 
 		open(splitDir+list2[i]); 
 		title=getTitle();
 		print(title);
 		getDimensions(width, height, channels, slices, frames);
 		// We use a specific function to extract the _z value from the file name
		zString = getSubstring(title+".tiff", "_z", "_");
		zValue = NaN; //or whatever to tell you that you could not read the value
		if(zString!="") {
   			zValue=parseInt(zString); //parseFloat if not always an integer value
			print (zValue);
		}		     	
 			for (j=1; j<=slices; j++){
 				run("Make Substack..."," slices="+j); 
  				saveAs("tif", dir2+title+"_"+IJ.pad(j, 3)+".tiff");
  				// The file name and z lavel of each focal plane are added to arrays. 
  				// The z spacing is calculated by dividing 1 / total number of focal planes.
    			Fname=Array.concat(title+"_"+IJ.pad(j, 3)+".tiff",Fname);
    			Zlayer=Array.concat(zValue,Zlayer);
    			zValue=zValue+(1/slices);
  				close();
 			}  
 		close();
 		}
 		 

//This produce the Z-project
list3 = getFileList(splitDir);
for (i=0; i<list3.length; i++) {
     if (endsWith(list3[i], ".tif")){
               print(i + ": " + dir+list3[i]);
             open(splitDir+list3[i]);
             imgName=File.nameWithoutExtension;
              print(imgName);
              getDimensions(width, height, channels, slices, frames);
              if (slices>1) {
              run("Z Project...", "projection=[Max Intensity]");
              saveAs("tif", Zdir+imgName+"MAX.tiff"); 
  			  close();	
  				}}}
  				
for (i = 0; i < Fname.length; i++) {
				setResult("name", i, Fname[i]);
    			setResult("X", i, "0");
    			setResult("Y", i, "0");
    			setResult("Z", i, Zlayer[i]);
}
saveAs("Results", dir2+"sequence"+".csv");   				
print("Done!");
 // la macro non aggiunge ad una result table che già esiste.. ma sovrascrive
 //qui alcuni spunti da esplorare http://imagej.1557.x6.nabble.com/how-to-append-results-in-excel-file-td5002126.html

// This function find a string 
function getSubstring(string, prefix, postfix) {
   start=indexOf(string, prefix)+lengthOf(prefix);
   end=start+indexOf(substring(string, start), postfix);
   if(start>=0&&end>=0)
     return substring(string, start, end);
   else
     return "";
}
