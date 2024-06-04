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
#  9.) Add right click to showArrows connections without selection button
# 10.) Save log to file with keypress
#           Store log as list of strings, which gets popped on undos
#
# Keyboard Controls:
# e colors green, q color purple, w toggles guess,
# s toggles variable "show", which determines if clicking a button 
# erases all arrows on screen, which is on by default, meaning that 
# arrows will not get erased when clicking,
# a show all arrows for all connections
# z undoes previous coloring
#
# Notes:
# Nothing will render above a button on a canvas, so placing text 
# widgets on top of buttons with their effective connections is not 
# possible.
# As such, the next best solution I could think of is to have a function 
# to toggle between making button text effective connections where possible 
# (which is when a button is green and has no purple children), and bins
#
#
# Effective Connections Notes:
# Undo():
#   If you are undoing a green coloring, iterate through parents,
#   if the parent has 0 effective connections (and it is not a contradiction), then do nothing
#   Otherwise increment effective connections of the parent
#   If you are undoing a purple, then undo green colorings for the children, and 
#   for any parents, if the parent is green, recalculate its effective connections
#   In either case, make the newly uncolored effective connections None
# 
# Throw contradiction if green has 0 effective connections without purple child.
# 
#
#
# Handling ∞:
# Every node has a boolean, infiniteEffConnections, that is true by default
# When it is true the effective connections will display ∞, although they 
# will be calculated as normal.
# When a node is colored purple, its combine on zero children's infiniteEffConnections 
# flags are made false
#
# Debug Notes:
# (1) Coloring a purple can color greens which cause other greens to have 0 effective 
#     connection with no purple child. This hould throw a contradiction, but currently 
#     doesn't
# (2) Change
# 
#
# Next Steps:
# We have 2 hash maps: one for history of colors, another for history of effective 
# connections. When color is changed, check that the respective hashmap has no entry
# for the key of the index of the button whose color is changed. If so, do not 
# append to the hashmap, if not, then append the color before the button's color 
# was changed to the hashmap. Effective connections is similar.
#
#
# To find if key is in hashmap use:
# if (col, row) not in hashMap:
#   hashMap[(col, row)] = oldValue



from tkinter import *
from tkinter.ttk import *
import numpy as np
import ctypes
import copy
import os
import datetime


path = os.getcwd()
clib = ctypes.CDLL(os.path.join(path, 'clibrary.so'))


# Edit parameters boxed below to edit the graph

#############################################################
                                                            #
# First index is the number of tokens in the first bin      #
# on the initial state                                      #
clib.build(14,0)                                            #
                                                            #
# Geometry variables                                        #
r = 5 # circle radius for base of arrows                    #
buttonWidth  = 100                                          #
buttonHeight = 30                                           #
grid_x       = 120 # grid spacing in x direction of buttons #
grid_y       = 50  # grid spacing in y direction of buttons #
windowWidth  = 1300                                         #
windowHeight = 450                                          #
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
        case "c":
            toggleEffectiveConnections()

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
def undo():
    global colorHistory
    global temp_style

    # Stop user from undoing past initial state
    if len(colorHistory) == 0:
        return 
    
    oldColors = colorHistory.pop()
    oldEffCons = effConHistory.pop()
 
    # Recolor and redisplay previous colors and effective connections
    for state in oldColors:
        buttons[state[0]][state[1]].configure(style=oldColors[state])
    for state in oldEffCons:
        buttons[state[0]][state[1]].configure(text=oldEffCons[state])
        if "," not in str(oldEffCons[state]) and oldEffCons[state] != "∞":
            eff_cons[state[0]][state[1]] = int(oldEffCons[state])
        else:
            eff_cons[state[0]][state[1]] = "∞"
    
    temp_style = "Light Blue.TButton"
    #buttons[oldColors[0][0]][oldColors[0][1]].configure(style=temp_style)  

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
        oldSelectedStyle = buttons[selected_button[0]][selected_button[1]]["style"]
        buttons[selected_button[0]][selected_button[1]].configure(style=oldSelectedStyle.removeprefix("BlueText"))
    
    showArrows(col,row, show)
    colorArrows(col,row)

    temp_style = buttons[col][row]["style"]
    buttons[col][row].configure(style="BlueText"+temp_style)
    selected_button = [col, row]


def colorArrows(col,row):

    if (selected_button != None):
        for arrow in arrows[selected_button[0]][selected_button[1]]:
            canvas.itemconfig(arrow, fill="white")
        for oval in ovals[selected_button[0]][selected_button[1]]:
            canvas.itemconfig(oval, outline="white") 

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
    global effConHistory

    # If you assign the same color to a button twice do nothing
    if (temp_style == color):
        return
    
    # Save button coloring before recoloring
    # colorHistory.append([[selected_button[0], selected_button[1], temp_style, None]])
    colorHistory.append({})
    colorHistory[-1][(selected_button[0], selected_button[1])] = temp_style
    effConHistory.append({})

    # Stop user from coloring already colored button another color
    if (temp_style != "Light Blue.TButton" and color != temp_style):
        buttons[selected_button[0]][selected_button[1]].configure(style="Red.TButton")
        print("Contradiction: Button", bins[selected_button[0]][selected_button[1]], "was", temp_style.replace(".TButton","").lower(), "so it cannot be", color.replace(".TButton","").lower())
        return
    
    # Color selected button
    buttons[selected_button[0]][selected_button[1]].configure(style=color)
    temp_style = color
    
    print("(", len(colorHistory),") Button", bins[selected_button[0]][selected_button[1]], "colored", color.replace(".TButton","").lower())

    if (color == "Green.TButton"):
        updateEffectiveGreen(selected_button[0], selected_button[1])

    stepCounter = 0
    if (color == "Purple.TButton"):

        # Compute effective connections of children of new purple
        removeInfiniteEffConsOfChildren(selected_button[0], selected_button[1])         

        children = clib.getChildren(selected_button[0], selected_button[1])
        for child_iter in range(children.size): 
            child = children.data[child_iter]
            colorGreen(child.col, child.row, stepCounter)

        parents = clib.getParents(selected_button[0], selected_button[1])
        for parent_iter in range(parents.size):  
            parent = parents.data[parent_iter]
            colorGreen(parent.col, parent.row, stepCounter)

        updateEffectivePurple(selected_button[0], selected_button[1])


def colorGreen(col, row, stepCounter):
    # Prevents recoloring green
    if "Green" in buttons[col][row]["style"]:
        return
    # Save child coloring before recoloring
    # colorHistory[-1].append([col, row, buttons[col][row]["style"], None])
    if (col, row) not in colorHistory[-1]:
        colorHistory[-1][(col, row)] = buttons[col][row]["style"]

    stepCounter = stepCounter+1
    if (buttons[col][row]["style"] == "Purple.TButton" or buttons[col][row]["style"] == "GuessPurple.TButton"):
        buttons[col][row].configure(style="Red.TButton")
        print("      (", len(colorHistory),".",stepCounter,") Contradiction: Button", bins[col][row], "was purple")
    else:
        buttons[col][row].configure(style="Green.TButton")
        print("      (", len(colorHistory),".",stepCounter,") Button", bins[col][row], "colored green")

    
def toggleGuess():
    global temp_style
    global colorHistory

    # Save button coloring before recoloring
    # colorHistory.append([[selected_button[0], selected_button[1], None, buttons[selected_button[0]][selected_button[1]]["text"]]])

    if selected_button == None or temp_style == "Light Blue.TButton": 
        return

    if "Guess" not in temp_style:
        # Save button coloring before recoloring
        if (col, row) not in colorHistory[-1]:
            colorHistory[-1][(col, row)] = buttons[selected_button[0]][selected_button[1]]["style"]
        buttons[selected_button[0]][selected_button[1]].configure(style="Guess"+temp_style)
        temp_style = "Guess"+temp_style


# Functions related to effective connections 
def toggleEffectiveConnections(): 
    global showEffectiveConnections
    global eff_cons

    if eff_cons:
        for col in eff_cons:
            for row in eff_cons:
                if len(eff_cons[col][row]) == 0:
                    continue
                buttons[col][row].configure(text=str(eff_cons[col][row]))
    eff_cons = not eff_cons


def updateEffectivePurple(col, row):
    # Make effective connections of parents 0
    parents = clib.getParents(col, row)
    for parent_iter in range(parents.size): 
        parent = parents.data[parent_iter]

        if (col, row) not in effConHistory[-1]:
            effConHistory[-1][(parent.col, parent.row)] = buttons[parent.col][parent.row]["text"]
        buttons[parent.col][parent.row].configure(text=str(0))
        eff_cons[parent.col][parent.row] = 0

    # Compute effective connections of parents of newly green children
    temp_history = copy.deepcopy(colorHistory[-1])
    for state in temp_history:
        if state == (col, row):
            continue
        updateEffectiveGreen(state[0], state[1])


def updateEffectiveGreen(col, row):

    # Decrement effective connections of parents of new green
    parents = clib.getParents(col, row)
    for parent_iter in range(parents.size):
        parent = parents.data[parent_iter]

        if eff_cons[parent.col][parent.row] == 0 or eff_cons[parent.col][parent.row] == "∞":
            continue

        
        if (eff_cons[parent.col][parent.row] == 1):
            print("Contradiction: Button", bins[col][row], "was colored green, lowering the effective connections of button", bins[parent.col][parent.row], "to 0 without a purple child")
            if (parent.col, parent.row) not in colorHistory[-1]:
                colorHistory[-1][(parent.col, parent.row)] = buttons[parent.col][parent.row]["style"]
            buttons[parent.col][parent.row].configure(style="Red.TButton")
            
        eff_cons[parent.col][parent.row] = eff_cons[parent.col][parent.row] - 1
        
        if "Green" in buttons[parent.col][parent.row]["style"] or "Red" in buttons[parent.col][parent.row]["style"]:
            # Save parent text before updating
            if (parent.col, parent.row) not in effConHistory[-1]:
                effConHistory[-1][(parent.col, parent.row)] = buttons[parent.col][parent.row]["text"]
            buttons[parent.col][parent.row].configure(text=str(eff_cons[parent.col][parent.row]))

    # Calculate effective connections of new green if it hasn't been done
    # eff_cons[col][row] = calcEffectiveConnections(col, row)

    # Save text before updating
    if (col, row) not in effConHistory[-1]:
        effConHistory[-1][(col, row)] = buttons[col][row]["text"]

    buttons[col][row].configure(text=str(eff_cons[col][row]))


def calcEffectiveConnections(col, row):
    
    if eff_cons[col][row] == "∞":
        return "∞"
    
    children = clib.getChildren(col, row)

    effectiveConnections = children.size
    for child_iter in range(children.size):
        child = children.data[child_iter]

        if "Purple" in buttons[child.col][child.row]["style"]:
            effectiveConnections = 0 
            break 
        elif "Green" in buttons[child.col][child.row]["style"]:
            effectiveConnections = effectiveConnections - 1
    
    return effectiveConnections

# def hasOtherPurpleParent(purpleCol, purpleRow, greenCol, greenRow): 
#     parents = clib.getParents(greenCol, greenRow)
#     for parent_iter in range(parents.size): 
#         parent = parents.data[parent_iter]
#         if (parent.col, parent.row) == 
#     return

def removeInfiniteEffConsOfChildren(col, row):
    children = clib.getChildren(col, row)
    for child_iter in range(children.size):
        child = children.data[child_iter]

        # If the child is a combine on 0 child, then give it finite effective connections
        if (checkCombineOnZero(col, row, child.col, child.row)):
            eff_cons[child.col][child.row] = None # Allows effective connections to be edited
            eff_cons[child.col][child.row] = calcEffectiveConnections(child.col, child.row)
        # Regardless of the if statement above, since this function is only called on purple 
        # colorings, we display the child's effective connections, because it is green
        #colorHistory[-1].append([child.col, child.row, "Green.TButton", buttons[child.col][child.row]["text"]])
        if (col, row) not in effConHistory[-1]:
            effConHistory[-1][(child.col, child.row)] = buttons[child.col][child.row]["text"]
        buttons[child.col][child.row].configure(text=str(eff_cons[child.col][child.row]))

def checkCombineOnZero(parentCol, parentRow, childCol, childRow):

    childSecondSmallestBin = int(bins[childCol][childRow].split(",")[-2:][0])
    currSecondSmallestBin  = int(bins[parentCol][parentRow].split(",")[-2:][0])
    diffSecondSmallest     = childSecondSmallestBin - currSecondSmallestBin

    childSmallestBin = int(bins[childCol][childRow].split(",")[-1:][0])
    currSmallestBin  = int(bins[parentCol][parentRow].split(",")[-1:][0])

    return diffSecondSmallest > 0 and currSmallestBin - childSmallestBin == 2*diffSecondSmallest

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


# For undo
colorHistory =  []
effConHistory = []

# Effective connections
eff_cons = [] 

# Strings in bins
bins = []

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
style.configure('TButton', bordercolor='black', borderwidth=3, font=('Helvetica', 11))

colors = ["Light Blue", "Green", "Purple", "Red"]
style.map('TButton',background=[('active',"dark grey")],foreground=[('active','black'),('!disabled',"black")])
for color in colors:

    style.configure(color+".TButton", bordercolor='black', borderwidth=3, font=('Helvetica', 11))
    style.map(color+".TButton",background=[("active","dark grey"),("!disabled",color)],foreground=[("active","black"),("!disabled","black")])

    style.configure("Guess"+color+".TButton", bordercolor='black', borderwidth=3, font=('Helvetica', 11))
    style.map("Guess"+color+".TButton",background=[("active","dark grey"),("!disabled",color)],foreground=[("active","red"),("!disabled","red")])

    style.configure("BlueText"+color+".TButton", bordercolor='blue', borderwidth=3, font=('Helvetica', 11))
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
         eff_cons.append([])
         bins.append([])
     col = state.location.col 
     row = state.location.row

     buttons[col].append(Button(canvas, style="Light Blue.TButton", text = tempBins, 
                                command = buttonClickedLambda(col, row), takefocus=True))
     arrows[col].append([])
     ovals[col].append([])
     eff_cons[col].append("∞")
     bins[col].append(tempBins)
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