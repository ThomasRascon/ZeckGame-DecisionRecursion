# TODO: 
# 1.) display move history (ex: move (2,3) colored green)
#     alternatively export history to text file 
#     Branch the history for guesses:
#          If you guess on move 18, call that move 18a, then the 
#          next move move 19a
# 2.) Clicking a node highlights forward connection and backward 
#     connection edges and nodes
# 3.) Generate with no connections/ toggle showing connections
# 4.) Click state to select, click color to color 
# 5.) Button for coloring all children and parents green (don't double color)
# 6.) Undo button (visually restore, and delete from history)
# 7.) Option for visually distinguishing guesses


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

# parents = clib.getParents(1,3)
# this gives you the "list" of the locations (as Pairs) of the parents of the
# state in (actual) position 1col, 3row
# for i in range(parents.size):
#     print(parents.data[i].col, parents.data[i].row)
# parents.data[i] gives you the ith parent of this state
# parents.data[i].col gives you the (actual) col of the ith parent of this state
# parents.data[i].row gives you the (actual) row of the ith parent of this state


# NOTE: state.bins[i] (the ith bin in state) is type ctypes.c_char
# must do ord(state.bins[i]) to turn into int and str(ord(state.bins[i]))
# to turn it into a string.
# The following block of code iterates through all states and prints out:
# 1. Their bins array and location in the graph (lines 66-71). Iterate
# through bins in reverse order to see most significant bit first
# which is the largest bin (see line 68).
# 2. The location of all of their parents (lines 73-76).
# 3. The location of all of their children (lines 78-81).
# while clib.moreStates():
#     state = clib.getState()
#     bins = ""
#     for i in range(state.size - 1, -1, -1):
#         bins += str(ord(state.bins[i])) + ","
#     bins = bins[:-1]
#     print(" ", bins, " ", state.location.col, state.location.row)

#     parents = clib.getParents(state.location.col, state.location.row)
#     print("    Parents:")
#     for i in range(parents.size):
#         print("     ", parents.data[i].col, parents.data[i].row)

#     children = clib.getChildren(state.location.col, state.location.row)
#     print("    Children:")
#     for i in range(children.size):
#         print("     ", children.data[i].col, children.data[i].row)


# columnHeight = clib.columnHeight(3)

bins = []
parents = []
children = []
tempCol = -1

clib.build(20,0)
while clib.moreStates():
     state = clib.getState()

     tempBins = ""
     for i in range(state.size - 1, -1, -1):
         tempBins += str(ord(state.bins[i])) + ","
     tempBins = tempBins[:-1]

     # Add new element for current bin
     # If we are on a new col, add new list 
     # for that col
     if tempCol != state.location.col:
         bins.append([])
         parents.append([])
         children.append([])
     tempCol = state.location.col 


     bins[state.location.col].append(tempBins)
     


def selectedLambda(row, col):
    return lambda: buttonClicked(row, col)

def giveColorLambda(color):
    return lambda: giveColor(color)

def buttonClicked(n, m):

    global yellow_button
    global temp_style
    global buttonWidth
    global buttonHeight
    global grid_x 
    global grid_y

    print("Button (", n, ", ", m, ") clicked")
    showArrows(n,m)

    # Overall, what these conditionals do is as follows:
        # If there was a yellow button when you clicked, 
        # return it to its original style
        # If the button you clicked was already yellow,
        # it has been set to its original color, so there 
        # is no longer a yellow button.
        # Otherwise save the clicked button's style and 
        # make it yellow

    if yellow_button != None:
        buttons[yellow_button[0]][yellow_button[1]].configure(style=temp_style)

    if yellow_button == [n,m]:
        yellow_button = None 
        return 
    else: 
        temp_style = buttons[n][m]["style"]
    
    buttons[n][m].configure(style="YellowBorder"+temp_style)
    yellow_button = [n, m]

def deleteArrows():
    
    for arrowColList in arrows:
        for arrowRowList in arrowColList:
            for arrow in arrowRowList:
                canvas.delete(arrow)
                
    for ovalColList in ovals:
        for ovalRowList in ovalColList:
            for oval in ovalRowList:
                canvas.delete(oval)

def showArrows(col,row):

    deleteArrows()
    
    children = clib.getChildren(col, row)
    #for connection in children[col][row]:
    for i in range(children.size):
        connection = children.data[i]

        
        A_x = (connection.col - col)*(grid_x)-.5*buttonWidth
        if connection.col == col:
            A_x = 0

        A_y = (connection.row - row)*(grid_y)
        
        a_y = buttonHeight*np.sign(A_y)/2
        if A_y == 0: 
            a_x = buttonWidth/2
        else:
            a_x = A_x*a_y/A_y 


        if a_x > buttonWidth/2:
            a_x = buttonWidth/2
            a_y = A_y*a_x/A_x
        

        circ_x = grid_x*col + buttonWidth/2 + a_x
        circ_y = grid_y*row + buttonHeight/2 + a_y
        ovals[col][row].append(canvas.create_oval(circ_x-r, circ_y-r, circ_x+r, circ_y+r))


        if col == connection.col and row < connection.row: # forward connection below
            arrows[col][row].append(canvas.create_line(col*grid_x+buttonWidth/2, row*grid_y+buttonHeight/2, connection.col*grid_x+buttonWidth/2, connection.row*grid_y, arrow=LAST))
        elif col == connection.col and row > connection.row: # forward connection above
            arrows[col][row].append(canvas.create_line(col*grid_x+buttonWidth/2, row*grid_y+buttonHeight/2, connection.col*grid_x+buttonWidth/2, connection.row*grid_y+buttonHeight, arrow=LAST))
        elif row == connection.row and col < connection.col: # forward connection to the right
            arrows[col][row].append(canvas.create_line(col*grid_x+buttonWidth/2, row*grid_y+buttonHeight/2, connection.col*grid_x, connection.row*grid_y+buttonHeight/2, arrow=LAST))
        elif (col < connection.col): # forward connection below to the right
            arrows[col][row].append(canvas.create_line(col*grid_x+buttonWidth/2, row*grid_y+buttonHeight/2, connection.col*grid_x, connection.row*grid_y+buttonHeight/2, arrow=LAST))

    parents = clib.getParents(col, row)
    for i in range(parents.size):
        connection = parents.data[i]
        
        A_x = (col - connection.col)*(grid_x)-.5*buttonWidth
        if connection.col == col:
            A_x = 0

        A_y = (row - connection.row)*(grid_y)
        
        a_y = buttonHeight*np.sign(A_y)/2
        if A_y == 0: 
            a_x = buttonWidth/2
        else:
            a_x = A_x*a_y/A_y 


        if a_x > buttonWidth/2:
            a_x = buttonWidth/2
            a_y = A_y*a_x/A_x
        
        circ_x = grid_x*connection.col + buttonWidth/2 + a_x
        circ_y = grid_y*connection.row + buttonHeight/2 + a_y
        ovals[col][row].append(canvas.create_oval(circ_x-r, circ_y-r, circ_x+r, circ_y+r))


        if col == connection.col and row < connection.row: # backward connection below
            arrows[col][row].append(canvas.create_line(connection.col*grid_x+buttonWidth/2, connection.row*grid_y+buttonHeight/2, col*grid_x+buttonWidth/2, row*grid_y+buttonHeight, arrow=LAST))
        elif col == connection.col and row > connection.row: # backward connection above
            arrows[col][row].append(canvas.create_line(connection.col*grid_x+buttonWidth/2, connection.row*grid_y+buttonHeight/2, col*grid_x+buttonWidth/2, row*grid_y+buttonHeight, arrow=LAST))
        elif row == connection.row and col > connection.col: # backward connection to the left
            arrows[col][row].append(canvas.create_line(connection.col*grid_x+buttonWidth/2, connection.row*grid_y+buttonHeight/2, col*grid_x, row*grid_y+buttonHeight/2, arrow=LAST))
        elif (col > connection.col): # forward connection above to the left
            arrows[col][row].append(canvas.create_line(connection.col*grid_x+buttonWidth/2, connection.row*grid_y+buttonHeight/2, col*grid_x, row*grid_y+buttonHeight/2, arrow=LAST))

         
    

def giveColor(color):

    global yellow_button
    global temp_style

    # If you assign the same color to a button twice, it becomes blue again
    if (temp_style == color):
        buttons[yellow_button[0]][yellow_button[1]].configure(style="Light Blue.TButton")
        yellow_button = None
        return
    
    temp_style = color
    buttons[yellow_button[0]][yellow_button[1]].configure(style=color)

    if (color == "Purple.TButton"):
       for connection in children[yellow_button[0]][yellow_button[1]]:
           if (buttons[connection.col][connection.row]["style"] == "Purple.TButton"):
               buttons[connection.col][connection.row].configure(style="Red.TButton")
           else:
               buttons[connection.col][connection.row].configure(style="Green.TButton")

    if (color != "Light Blue.TButton" and color != temp_style):
        buttons[yellow_button[0]][yellow_button[1]].configure(style="Red.TButton")

    yellow_button = None

   

def toggleGuess():
    global temp_style

    if yellow_button == None or temp_style == "Light Blue.TButton": 
        return

    if "Guess" in temp_style:
        buttons[yellow_button[0]][yellow_button[1]].configure(style=temp_style.lstrip("Guess")) 
    else: 
        buttons[yellow_button[0]][yellow_button[1]].configure(style="Guess"+temp_style)
        temp_style = "Guess"+temp_style

def on_scrolly(*args):
    canvas.yview(*args)

def on_scrollx(*args):
    canvas.xview(*args)

def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))




col_tot = len(bins)
row_tot = 1000
r = 5 # circle radius for base of arrows
buttonHeight = 30
buttonWidth = 100
grid_x = 120
grid_y = 50

buttons = [[None]*row_tot for i in range(col_tot)]
button_frames = []
connections = [[[]]*row_tot for i in range(col_tot)]
arrows = [[[]]*row_tot for i in range(col_tot)]
ovals =  [[[]]*row_tot for i in range(col_tot)]



yellow_button = None
selected_button = None
temp_style = None


# Create primary window
root = Tk()
root.geometry("1000x500")
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

    style.configure("YellowBorder"+color+".TButton", bordercolor='magenta', borderwidth=3, font=('Helvetica', 10))
    style.map("YellowBorder"+color+".TButton",background=[("active","dark grey"),("!disabled",color)],foreground=[("active","black"),("!disabled","black")])

# Create and place buttons
for col in range(len(bins)):
    buttons.append([])
    for row in range (len(bins[col])):
        buttons[col].append([])

        # to change button text to indices replace argument of text with 
        # 
        buttons[col][row] = Button(canvas, style="Light Blue.TButton", text = bins[col][row], 
                                  command = selectedLambda(col, row), takefocus=True)
        buttons[col][row].grid(row=0, column=0)

        # This is needed to make buttons scrollable
        canvas.create_window((grid_x*col, grid_y*row), window=buttons[col][row], height=buttonHeight, width=buttonWidth, anchor="nw")   

        # uncomment to see all connections on initialization
        # showArrows(col,row)



# Create secondary window
root2 = Toplevel(root)
root2.geometry("270x35")
root2.attributes('-topmost',True) # This keeps the secondary window permanently on top

# Secondary window buttons
colorGreen = Button(root2, style="Green.TButton", text = "Color Green", 
                    command = giveColorLambda("Green.TButton"))
colorPurple = Button(root2, style="Purple.TButton", text = "Color purple", 
                    command = giveColorLambda("Purple.TButton"))
textToggler = Button(root2, text = "Flag Guess", 
                    command = toggleGuess)  

 

colorGreen.grid(row=1, column=1, padx=3)
colorPurple.grid(row=1, column=2, padx=3)
textToggler.grid(row=1, column=3, padx=3)

               
root.mainloop()

clib.deallocate()