# TODO: 
# 1.) display move history (ex: move (2,3) colored green)
#     alternatively export history to text file 
#     Branch the history for guesses:
#          If you guess on move 18, call that move 18a, then the 
#          next move move 19a
# 2.) Clicking a node highlights forward connection and backward 
#     connection edges and nodes
#[3.)] Generate with no connections/ toggle showing connections
#[4.)]Click state to select, click color to color 
#[5.)]Button for coloring all children and parents green (don't double color)
# 6.) Undo button (visually restore, and delete from history)
#[7.)]Option for visually distinguishing guesses
#
# Keyboard Controls:
# z colors green, x color purple, c toggles guess,
# s toggles variable "show", which determines if clicking a button 
# erases all arrows on screen, which is on by default, meaning that 
# arrows will not get erased when clicking,
# a shows all arrows for all connections


from tkinter import *
from tkinter.ttk import *
import numpy as np
import ctypes
import os

path = os.getcwd()
clib = ctypes.CDLL(os.path.join(path, 'clibrary.so'))

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

# First index is the number of tokens in the first bin 
# on the initial state
clib.build(11,0)

# Keyboard controlled events
def keyPressed(event):
    
    global show
    
    match event.char:
        case "z":
            giveColor("Green.TButton")
        case "x":
            giveColor("Purple.TButton")
        case "c":
            toggleGuess()
        case "s": # toggle show
            show = not show
        case "a": 
            showAllArrows()

# Functions related to arrow and button placement 

def button_x(col, row):
    col*grid_x

def button_y(col, row):
    row*grid_y

def deleteArrows():
    
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
    
    children = clib.getChildren(col, row)
    for i in range(children.size):
        child = children.data[i]

        # maxColHeight-colHeight+row
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


    parents = clib.getParents(col, row)
    for i in range(parents.size):
        parent = parents.data[i]
        

        # maxColHeight-colHeight+row
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


def showAllArrows():
    for col in range(len(buttons)):
        for row in range(len(buttons[col])):
            showArrows(col,row,True)


# Functions related to styling 
def buttonClickedLambda(row, col):
    return lambda: buttonClicked(row, col)

def buttonClicked(n, m):

    global selected_button
    global temp_style
    global buttonWidth
    global buttonHeight
    global grid_x 
    global grid_y
    global show

    print("Button (", n, ", ", m, ") clicked")
    showArrows(n,m, show)
    colorArrows(n,m)

    # Overall, what these conditionals do is as follows:
        # If there was a yellow button when you clicked, 
        # return it to its original style
        # If the button you clicked was already yellow,
        # it has been set to its original color, so there 
        # is no longer a yellow button.
        # Otherwise save the clicked button's style and 
        # make it yellow

    if selected_button != None:
        buttons[selected_button[0]][selected_button[1]].configure(style=temp_style)

    if selected_button == [n,m]:
        selected_button = None 
        return 
    else: 
        temp_style = buttons[n][m]["style"]
    
    buttons[n][m].configure(style="YellowBorder"+temp_style)
    selected_button = [n, m]


def colorArrows(n,m):

    if (selected_button != None):
        for arrow in arrows[selected_button[0]][selected_button[1]]:
            canvas.itemconfig(arrow, fill="white")
        for oval in ovals[selected_button[0]][selected_button[1]]:
            canvas.itemconfig(oval, outline="white") 
        
    for arrow in arrows[n][m]:
        canvas.itemconfig(arrow, fill="blue")
    for oval in ovals[n][m]:
        canvas.itemconfig(oval, outline="blue") 
    
    

def giveColorLambda(color):
    return lambda: giveColor(color)

def giveColor(color):

    global selected_button
    global temp_style

    # If you assign the same color to a button twice, it becomes blue again
    if (temp_style == color):
        buttons[selected_button[0]][selected_button[1]].configure(style="Light Blue.TButton")
        # selected_button = None
        return
    
    temp_style = color
    buttons[selected_button[0]][selected_button[1]].configure(style=color)

    if (color == "Purple.TButton"):
        children = clib.getChildren(selected_button[0], selected_button[1])
        for i in range(children.size):  
           connection = children.data[i]
           if (buttons[connection.col][connection.row]["style"] == "Purple.TButton"):
               buttons[connection.col][connection.row].configure(style="Red.TButton")
           else:
               buttons[connection.col][connection.row].configure(style="Green.TButton")

    if (color != "Light Blue.TButton" and color != temp_style):
        buttons[selected_button[0]][selected_button[1]].configure(style="Red.TButton")

    #selected_button = None


def toggleGuess():
    global temp_style

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

# Geometry variables
r = 5 # circle radius for base of arrows
buttonHeight = 30
buttonWidth = 100
grid_x = 120 # grid spacing in x direction of buttons
grid_y = 50  # grid spacing in y direction of buttons

# Lists of widgets
buttons = []
button_frames = []
arrows = []
ovals =  []

# Selected button variables
selected_button = None
temp_style = None

# If this is false, then clicking on one button deletes 
# arrows of all other buttons
show = True


# Create primary window
root = Tk()
root.geometry("1200x500")
root.configure(background="light grey")


# Create Scrollbar widgets
scrollbary = Scrollbar(root, orient="vertical", command=on_scrolly)
scrollbary.pack(side="right", fill="y")

scrollbarx = Scrollbar(root, orient="horizontal", command=on_scrollx)
scrollbarx.pack(side="bottom", fill="x")

# Create a Canvas widget
canvas = Canvas(root, bg="grey")
canvas.pack(side="top", fill="both", expand=True)


# Configure the Canvas and Scrollbars
canvas.config(yscrollcommand=scrollbary.set)
scrollbary.config(command=on_scrolly)

canvas.config(xscrollcommand=scrollbarx.set)
scrollbarx.config(command=on_scrollx)

canvas.bind("<Configure>", on_configure)


style = Style()
style.theme_use("clam")

# Add styles
style.configure('TButton', bordercolor='black', borderwidth=3)

colors = ["Light Blue", "Green", "Purple", "Red"]
style.map('TButton',background=[('active',"dark grey")],foreground=[('active','black'),('!disabled',"black")])
for color in colors:

    style.configure(color+".TButton", bordercolor='black', borderwidth=3, font=('Helvetica', 10))
    style.map(color+".TButton",background=[("active","dark grey"),("!disabled",color)],foreground=[("active","black"),("!disabled","black")])

    style.configure("Guess"+color+".TButton", bordercolor='black', borderwidth=3, font=('Helvetica', 10))
    style.map("Guess"+color+".TButton",background=[("active","dark grey"),("!disabled",color)],foreground=[("active","red"),("!disabled","red")])

    style.configure("YellowBorder"+color+".TButton", bordercolor='blue', borderwidth=3, font=('Helvetica', 10))
    style.map("YellowBorder"+color+".TButton",background=[("active","dark grey"),("!disabled",color)],foreground=[("active","black"),("!disabled","black")])


# Make and place buttons, and make arrays for circles and arrows
col = -1
while clib.moreStates():
     state = clib.getState()
     

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
     col = state.location.col 
     row = state.location.row

     buttons[col].append(Button(canvas, style="Light Blue.TButton", text = tempBins, 
                                command = buttonClickedLambda(col, row), takefocus=True))
     arrows[col].append([])
     ovals[col].append([])


maxColHeight = max([clib.columnHeight(col) for col in range(len(buttons))])

for col in range(len(buttons)):
     for row in range(len(buttons[col])):
        colHeight = len(buttons[col])
     # This is needed to make buttons scrollable
        buttons[col][row].grid(row=0, column=0)
        canvas.create_window((grid_x*col, grid_y*(maxColHeight-colHeight+row)), window=buttons[col][row], height=buttonHeight, width=buttonWidth, anchor="nw")

# Show all arrows on initialization  
showAllArrows()

# Enables keyboard input
# See keyPressed method for result of inputs
root.bind("<KeyPress>", keyPressed)
               
root.mainloop()

clib.deallocate()