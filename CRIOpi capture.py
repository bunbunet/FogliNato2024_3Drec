import curses
import picamera
import time

print("Keyboard control: \n DOWN = start preview \n SpaceBar = Take picture \n a,s = increase,decrease series number \z,x = increase,decrease section number\nq = leave")
Name = raw_input("Specimen Name: ");
number_of_pz = int(raw_input("Number of Series: ")); 
                    
#number_of_pz = 6
camera=picamera.PiCamera()
pics_taken = 0
section = 1
pz = 1

camera.resolution = (1920, 1080)
camera.rotation = 180

# Get the curses window, turn off echoing of keyboard to screen, turn on
# instant (no waiting) key response, and use special values for cursor keys
screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)


def take_pic():
    global pics_taken
    global pz
    pics_taken += 1
    pz +=1
    series=pz-1
    camera.capture(Name +"_z"+ str(pics_taken) + "_"+str(section) + "_series_"+str(series)+'.png')

try:
        while True:
            if pz == number_of_pz + 1:
                pz = 1
                section +=1
            camera.annotate_text = "Sections_" + str(pics_taken) +"; Series Section_"+ str(section) + "; Pz_"+str(pz)
            char = screen.getch()
            if char == ord('q'):
                break
            elif char ==ord('s'):
                pz=(pz+1)
            elif char ==ord('a'):
                pz=(pz-1)
            elif char ==ord('z'):
                section = (section -1)
            elif char ==ord('x'):
                section = (section +1)
            elif char ==ord(' '):
                take_pic()
            elif char == curses.KEY_UP:
                take_pic()
            elif char == curses.KEY_DOWN:
                camera.start_preview()
finally:
    #Close down curses properly, inc turn echo back on!
        curses.nocbreak(); screen.keypad(0); curses.echo()
        curses.endwin()
