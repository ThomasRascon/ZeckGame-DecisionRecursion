# TODO: 
# [1.)]display move history (ex: move (2,3) colored green)
#     alternatively export history to text file 
#     Branch the history for guesses:
#          If you guess on move 18, call that move 18a, then the 
#          next move move 19a
# [2.)]Clicking a node highlights forward connection and backward 
#     connection edges and nodes
# [3.)] Generate with no connections/ toggle showing connections
# [4.)]Click state to select, click color to color 
# [5.)]Button for coloring all children and parents green (don't double color)
# [6.)]Undo button (visually restore, and delete from history)
# [7.)]Option for visually distinguishing guesses
#  8.) Display effective connections, and whether a button has a purple child
#  9.) Add right click to show connections without selection button
# 10.) Save log to file with keypress
#           Store log as list of strings, which gets popped on undos
#
# Keyboard Controls:
# e colors green, q color purple, w toggles guess,
# s toggles variable "show", which determines if clicking a button 
# erases all arrows on screen, which is on by default, meaning that 
# arrows will not get erased when clicking,
# a shows all arrows for all connections
# z undoes previous coloring
#
# Notes:
# Nothing will render above a button on a canvas, so placing text 
# widgets on top of buttons with their effective connections is not 
# possible.
# As such, the next best solution I could think of is to have a function 
# to toggle between making button text effective connections where possible 
# (which is when a button is green and has no purple children), and bins


from tkinter import *
from tkinter.ttk import *
import numpy as np
import ctypes
import os
import datetime



path = os.getcwd()
clib = ctypes.CDLL(os.path.join(path, 'clibrary.so'))


# Edit parameters boxed below to edit the graph

#############################################################
                                                            #
# First index is the number of tokens in the first bin      #
# on the initial state                                      #
clib.build(10,0)                                            #
                                                            #
# Geometry variables                                        #
r = 5 # circle radius for base of arrows                    #
buttonWidth  = 100                                          #
buttonHeight = 30                                           #
grid_x       = 120 # grid spacing in x direction of buttons #
grid_y       = 50  # grid spacing in y direction of buttons #
windowWidth  = 1000                                         #
windowHeight = 400                                          #
                                                            #
#############################################################

# Definitions of clib functions
class Pair(ctypes.Structure):
    _fields_ = [("col", ctypes.c_int), ("row", ctypes.c_int)]

class PairVector(ctypes.Structure):
    _fields_ = [("data", ctypes.POINTER(Pair)),
                ("size", ctypes.c_size_t)]

class State(ctypes.Structure):
    _fields_ = [("bins", ctypes.POINTER(ctypes.c_char)),
                ("size", ctypes.c_size_t),
                ("location", Pair)]

clib.build.argtypes = [ctypes.c_int, ctypes.c_int]
clib.getParents.argtypes = [ctypes.c_int, ctypes.c_int]
clib.getChildren.argtypes = [ctypes.c_int, ctypes.c_int]
clib.columnHeight.argtypes = [ctypes.c_int]

clib.getParents.restype = PairVector
clib.getChildren.restype = PairVector
clib.getState.restype = State
clib.columnHeight.restype = ctypes.c_int


# Keyboard controlled events
def keyPressed(event):
    global show
    
    match event.char:
        case "e":
            giveColor("Green.TButton")
        case "q":
            giveColor("Purple.TButton")
        case "w":
            toggleGuess()
        case "s": # toggle show
            show = not show
        case "a": 
            showAllArrows()
        case "z":
            undo()

# Functions related to arrow and oval generation
def deleteArrows():
    global allArrowsShown 

    allArrowsShown = False 

    for arrowColList in arrows:
        for arrowRowList in arrowColList:
            for arrow in arrowRowList:
                canvas.delete(arrow)
                
    for ovalColList in ovals:
        for ovalRowList in ovalColList:
            for oval in ovalRowList:
                canvas.delete(oval)


def showArrows(col,row,show):
    if not show:
        deleteArrows()

    makeChildArrows(col, row)
    makeParentArrows(col, row)


def showAllArrows():
    global allArrowsShown 

    # Prevents duplicates of arrows due to repeated calls
    if allArrowsShown: 
        return 
    allArrowsShown = True

    timeStart = datetime.datetime.now() # debug
    for col in range(len(buttons)):
        for row in range(len(buttons[col])):
            makeParentArrows(col, row)
    # debug
    timeElapsed = datetime.datetime.now() - timeStart 
    print("showAllArrows took: ", timeElapsed)


def makeChildArrows(col, row): 
    children = clib.getChildren(col, row)
    for i in range(children.size):
        child = children.data[i]

        colHeightChild = len(buttons[child.col])
        colHeightButton = len(buttons[col])

        if col == child.col and row < child.row: # forward child below
            arrowStart_x = col*grid_x+buttonWidth/2
            arrowStart_y = (maxColHeight-colHeightButton+row)*grid_y+buttonHeight/2
            arrowEnd_x   = child.col*grid_x+buttonWidth/2
            arrowEnd_y   = (maxColHeight-colHeightChild+child.row)*grid_y
        elif col == child.col and row > child.row: # forward child above
            arrowStart_x = col*grid_x+buttonWidth/2
            arrowStart_y = (maxColHeight-colHeightButton+row)*grid_y+buttonHeight/2
            arrowEnd_x   = child.col*grid_x+buttonWidth/2
            arrowEnd_y   = (maxColHeight-colHeightChild+child.row)*grid_y+buttonHeight
        elif row == child.row and col < child.col: # forward child to the right
            arrowStart_x = col*grid_x+buttonWidth/2
            arrowStart_y = (maxColHeight-colHeightButton+row)*grid_y+buttonHeight/2
            arrowEnd_x   = child.col*grid_x
            arrowEnd_y   = (maxColHeight-colHeightChild+child.row)*grid_y+buttonHeight/2
        elif (col < child.col): # forward child below to the right
            arrowStart_x = col*grid_x+buttonWidth/2
            arrowStart_y = (maxColHeight-colHeightButton+row)*grid_y+buttonHeight/2
            arrowEnd_x   = child.col*grid_x
            arrowEnd_y   = (maxColHeight-colHeightChild+child.row)*grid_y+buttonHeight/2

        arrows[col][row].append(canvas.create_line(arrowStart_x, arrowStart_y , arrowEnd_x, arrowEnd_y, arrow=LAST, fill="white"))

        # Oval placement geometry
        A_x = arrowEnd_x - arrowStart_x
        A_y = arrowEnd_y - arrowStart_y
        
        a_y = buttonHeight*np.sign(A_y)/2
        if A_y == 0: 
            a_x = buttonWidth/2
        else:
            a_x = A_x*a_y/A_y 

        if a_x > buttonWidth/2:
            a_x = buttonWidth/2
            a_y = A_y*a_x/A_x
        
        circ_x = grid_x*col + buttonWidth/2 + a_x
        circ_y = grid_y*(maxColHeight-colHeightButton+row) + buttonHeight/2 + a_y
        ovals[col][row].append(canvas.create_oval(circ_x-r, circ_y-r, circ_x+r, circ_y+r, outline="white"))


def makeParentArrows(col, row):
    parents = clib.getParents(col, row)
    for i in range(parents.size):
        parent = parents.data[i]

        colHeightParent = len(buttons[parent.col])
        colHeightButton = len(buttons[col])

        if col == parent.col and row < parent.row: # backward parent below
            arrowStart_x = parent.col*grid_x+buttonWidth/2
            arrowStart_y = (maxColHeight-colHeightParent+parent.row)*grid_y+buttonHeight/2
            arrowEnd_x   = col*grid_x+buttonWidth/2
            arrowEnd_y   = (maxColHeight-colHeightButton+row)*grid_y+buttonHeight
            
        elif col == parent.col and row > parent.row: # backward parent above
            arrowStart_x = parent.col*grid_x+buttonWidth/2
            arrowStart_y = (maxColHeight-colHeightParent+parent.row)*grid_y+buttonHeight/2
            arrowEnd_x   = col*grid_x+buttonWidth/2
            arrowEnd_y   = (maxColHeight-colHeightButton+row)*grid_y+buttonHeight
        elif row == parent.row and col > parent.col: # backward parent to the left
            arrowStart_x = parent.col*grid_x+buttonWidth/2
            arrowStart_y = (maxColHeight-colHeightParent+parent.row)*grid_y+buttonHeight/2
            arrowEnd_x   = col*grid_x
            arrowEnd_y   = (maxColHeight-colHeightButton+row)*grid_y+buttonHeight/2
        elif (col > parent.col): # backward parent above to the left
            arrowStart_x = parent.col*grid_x+buttonWidth/2
            arrowStart_y = (maxColHeight-colHeightParent+parent.row)*grid_y+buttonHeight/2
            arrowEnd_x   = col*grid_x
            arrowEnd_y   = (maxColHeight-colHeightButton+row)*grid_y+buttonHeight/2

        arrows[col][row].append(canvas.create_line(arrowStart_x, arrowStart_y , arrowEnd_x, arrowEnd_y, arrow=LAST, fill="white"))

        # Oval placement geometry
        A_x = arrowEnd_x - arrowStart_x
        A_y = arrowEnd_y - arrowStart_y
        
        a_y = buttonHeight*np.sign(A_y)/2
        if A_y == 0: 
            a_x = buttonWidth/2
        else:
            a_x = A_x*a_y/A_y 

        if a_x > buttonWidth/2:
            a_x = buttonWidth/2
            a_y = A_y*a_x/A_x

        circ_x = grid_x*parent.col + buttonWidth/2 + a_x
        circ_y = grid_y*(maxColHeight-colHeightParent+parent.row) + buttonHeight/2 + a_y
        ovals[col][row].append(canvas.create_oval(circ_x-r, circ_y-r, circ_x+r, circ_y+r, outline="white"))

# Functions related to styling 
def getAllColors():
    allColors = []
    for col in range(len(buttons)):
        allColors.append([])
        for button in buttons[col]:
            allColors[col].append(button["style"])

    if selected_button != None:
        allColors[selected_button[0]][selected_button[1]] = temp_style

    return allColors

def undo():
    global colorHistory
    global temp_style

    if len(colorHistory) == 0:
        return 
    oldColors = colorHistory.pop()

    if selected_button != None:
        temp_style = oldColors[0][2]

    for state in oldColors:
        buttons[state[0]][state[1]].configure(style=state[2])

    buttons[selected_button[0]][selected_button[1]].configure(style="BlueText"+temp_style)
    print("Undo")

def buttonClickedLambda(col, row):
    return lambda: buttonClicked(col, row)

def buttonClicked(col, row):
    global selected_button
    global temp_style
    global buttonWidth
    global buttonHeight
    global grid_x 
    global grid_y
    global show

    # print("Button (", buttons[col][row]["text"], ") clicked")
    

    # Overall, what these conditionals do is as follows:
        # If there was a selected button when you clicked, 
        # return it to its original style, called temp_style.
        # If the button you clicked was already selected,
        # do nothing. Consider this case to be user error.
        # Otherwise save the clicked button's style as temp_style 
        # and make it selected

    if selected_button == [col,row]:
        return
    
    if selected_button != None:
        buttons[selected_button[0]][selected_button[1]].configure(style=temp_style)
    
    temp_style = buttons[col][row]["style"]
    
    showArrows(col,row, show)
    colorArrows(col,row)

    buttons[col][row].configure(style="BlueText"+temp_style)
    selected_button = [col, row]


def colorArrows(col,row):

    if (selected_button != None):
        for arrow in arrows[selected_button[0]][selected_button[1]]:
            canvas.itemconfig(arrow, fill="brown")
        for oval in ovals[selected_button[0]][selected_button[1]]:
            canvas.itemconfig(oval, outline="brown") 

    selected_color = "blue"
    for arrow in arrows[col][row]:
        canvas.itemconfig(arrow, fill=selected_color)
    for oval in ovals[col][row]:
        canvas.itemconfig(oval, outline=selected_color) 


def giveColorLambda(color):
    return lambda: giveColor(color)

def giveColor(color):
    global selected_button
    global temp_style
    global colorHistory

    # If you assign the same color to a button twice do nothing
    if (temp_style == color):
        return
    
    # Save button coloring before recoloring
    colorHistory.append([[selected_button[0], selected_button[1], temp_style]])

    # Stop user from coloring already colored button another color
    if (temp_style != "Light Blue.TButton" and color != temp_style):
        buttons[selected_button[0]][selected_button[1]].configure(style="Red.TButton")
        print("Contradiction: Button", buttons[selected_button[0]][selected_button[1]]["text"], "was", temp_style.replace(".TButton","").lower(), "so it cannot be", color.replace(".TButton","").lower())
        return
    
    # Color selected button
    buttons[selected_button[0]][selected_button[1]].configure(style=color)
    temp_style = color
    
    print("(", len(colorHistory),") Button", buttons[selected_button[0]][selected_button[1]]["text"], "colored", color.replace(".TButton","").lower())

    stepCounter = 0
    if (color == "Purple.TButton"):
        children = clib.getChildren(selected_button[0], selected_button[1])
        for i in range(children.size):  
           connection = children.data[i]
           # Save child coloring before recoloring
           colorHistory[-1].append([connection.col, connection.row, buttons[connection.col][connection.row]["style"]])

           stepCounter = stepCounter+1
           if (buttons[connection.col][connection.row]["style"] == "Purple.TButton" or buttons[connection.col][connection.row]["style"] == "GuessPurple.TButton"):
               buttons[connection.col][connection.row].configure(style="Red.TButton")
               print("      (", len(colorHistory),".",stepCounter,") Contradiction: Button", buttons[connection.col][connection.row]["text"], "was purple")
           else:
               buttons[connection.col][connection.row].configure(style="Green.TButton")
               print("      (", len(colorHistory),".",stepCounter,") Button", buttons[connection.col][connection.row]["text"], "colored green")


def toggleGuess():
    global temp_style
    global colorHistory

    # Save button coloring before recoloring
    colorHistory.append([[selected_button[0], selected_button[1], buttons[selected_button[0]][selected_button[1]]["style"]]])

    if selected_button == None or temp_style == "Light Blue.TButton": 
        return

    if "Guess" in temp_style:
        buttons[selected_button[0]][selected_button[1]].configure(style=temp_style.lstrip("Guess")) 
    else: 
        buttons[selected_button[0]][selected_button[1]].configure(style="Guess"+temp_style)
        temp_style = "Guess"+temp_style

# Functions related to scrolling
def on_scrolly(*args):
    canvas.yview(*args)

def on_scrollx(*args):
    canvas.xview(*args)

def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

# End functions


# Lists of widgets
buttons = []
button_frames = []
arrows = []
ovals =  []
ef_cons = [] # Effective connections

# For undo
colorHistory = []

# Selected button variables
selected_button = None # 1D list of length 2. 0th index is col, 1st index is row
temp_style = None # Style of selected button it should be when another button is selected

# If this is false, then clicking on one button deletes 
# arrows of all other buttons.
# Otherwise arrows generated will stay on screen until 
# this variable is made false and a button is clicked.
show = True

# Create primary window
root = Tk()
root.geometry(str(windowWidth)+"x"+str(windowHeight))
root.configure(background="light grey")

# Create Scrollbar widgets
scrollbary = Scrollbar(root, orient="vertical", command=on_scrolly)
scrollbary.pack(side="right", fill="y")

scrollbarx = Scrollbar(root, orient="horizontal", command=on_scrollx)
scrollbarx.pack(side="bottom", fill="x")

# Create a Canvas widget
canvas = Canvas(root, bg="light grey")
canvas.pack(side="top", fill="both", expand=True)

# Configure the Canvas and Scrollbars
canvas.config(yscrollcommand=scrollbary.set)
scrollbary.config(command=on_scrolly)

canvas.config(xscrollcommand=scrollbarx.set)
scrollbarx.config(command=on_scrollx)

canvas.bind("<Configure>", on_configure)

# Define overall theme
style = Style()
style.theme_use("clam")

# Add styles
style.configure('TButton', bordercolor='black', borderwidth=3, font=('Helvetica', 10))

colors = ["Light Blue", "Green", "Purple", "Red"]
style.map('TButton',background=[('active',"dark grey")],foreground=[('active','black'),('!disabled',"black")])
for color in colors:

    style.configure(color+".TButton", bordercolor='black', borderwidth=3, font=('Helvetica', 10))
    style.map(color+".TButton",background=[("active","dark grey"),("!disabled",color)],foreground=[("active","black"),("!disabled","black")])

    style.configure("Guess"+color+".TButton", bordercolor='black', borderwidth=3, font=('Helvetica', 10))
    style.map("Guess"+color+".TButton",background=[("active","dark grey"),("!disabled",color)],foreground=[("active","red"),("!disabled","red")])

    style.configure("BlueText"+color+".TButton", bordercolor='blue', borderwidth=3, font=('Helvetica', 10))
    style.map("BlueText"+color+".TButton",background=[("active","dark grey"),("!disabled",color)],foreground=[("active","blue"),("!disabled","blue")])


# Make buttons, and arrays for circles and arrows
timeStart = datetime.datetime.now() # debug 

col = -1
while clib.moreStates():
     state = clib.getState()
     
     # Make string with bins
     tempBins = ""
     for i in range(state.size - 1, -1, -1):
         tempBins += str(ord(state.bins[i])) + ","
     tempBins = tempBins[:-1]

     # Add new element for current bin
     # If we are on a new col, add new list 
     # for that col
     if col != state.location.col:
         buttons.append([])
         arrows.append([])
         ovals.append([])
         ef_cons.append([])
     col = state.location.col 
     row = state.location.row

     buttons[col].append(Button(canvas, style="Light Blue.TButton", text = tempBins, 
                                command = buttonClickedLambda(col, row), takefocus=True))
     arrows[col].append([])
     ovals[col].append([])
     ef_cons[col].append(None)
# debug
timeElapsed = datetime.datetime.now() - timeStart 
print("Making arrays took: ", timeElapsed)

# Place buttons
timeStart = datetime.datetime.now() # debug

maxColHeight = max([clib.columnHeight(col) for col in range(len(buttons))])
for col in range(len(buttons)):
     for row in range(len(buttons[col])):
        colHeight = len(buttons[col])
     # This is needed to make buttons scrollable
        buttons[col][row].grid(row=0, column=0)
        canvas.create_window((grid_x*col, grid_y*(maxColHeight-colHeight+row)), window=buttons[col][row], height=buttonHeight, width=buttonWidth, anchor="nw")
# debug
timeElapsed = datetime.datetime.now() - timeStart 
print("Placing buttons took: ", timeElapsed)

# Show all arrows on initialization  
allArrowsShown = False 
showAllArrows()
allArrowsShown = True

# Enables keyboard input
# See keyPressed method for result of inputs
root.bind("<KeyPress>", keyPressed)

# Starts canvas scrolled all the way down
canvas.update_idletasks()
canvas.yview_moveto(1)

root.mainloop()


timeStart = datetime.datetime.now() # debug

clib.deallocate()
# debug
timeElapsed = datetime.datetime.now() - timeStart 
print("clib.deallocate() took: ", timeElapsed)