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


def selectedLambda(row, col):
    return lambda: buttonClicked(row, col)

def giveColorLambda(color):
    return lambda: giveColor(color)

def buttonClicked(n, m):

    global yellow_button
    global temp_style

    print("Button (", n, ", ", m, ") clicked")

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
    
    buttons[n][m].configure(style="yellow.TButton")
    yellow_button = [n, m]
    

def giveColor(color):
    global yellow_button
    global temp_style
    print(temp_style)

    # If you assign the same color to a button twice, it becomes blue again
    if (temp_style == color):
        buttons[yellow_button[0]][yellow_button[1]].configure(style="Light Blue.TButton")
        yellow_button = None
        return
    
    temp_style = color
    buttons[yellow_button[0]][yellow_button[1]].configure(style=color)
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




col_tot = 10
row_tot = 10
r = 3 # circle radius for base of arrows

buttons = [[None]*row_tot for i in range(col_tot)]
button_frames = []
connections = [[[]]*row_tot for i in range(col_tot)]
arrows = [[None]*row_tot for i in range(col_tot)]



yellow_button = None
selected_button = None
temp_style = None


# Create primary window
root = Tk()
root.geometry("400x400")
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

colors = ["yellow", "Light Blue", "Green", "Purple", "Red"]
style.map('TButton',background=[('active',"dark grey")],foreground=[('active','black'),('!disabled',"black")])
for color in colors:

    style.configure(color+".TButton", bordercolor='black', borderwidth=3)
    style.map(color+".TButton",background=[("active","dark grey"),("!disabled",color)],foreground=[("active","black"),("!disabled","black")])

    style.configure("Guess"+color+".TButton", bordercolor='red', borderwidth=3)
    style.map("Guess"+color+".TButton",background=[("active","dark grey"),("!disabled",color)],foreground=[("active","black"),("!disabled","black")])


# Create and place buttons
for col in range(col_tot):
    for row in range (row_tot):
        
        buttons[col][row] = Button(canvas, style="Light Blue.TButton", text = "button "+ str(col) + ", " + str(row), 
                                  command = selectedLambda(col, row), takefocus=True)
        buttons[col][row].place(x=100*col, y= 50*row)

        # This is needed to make buttons scrollable
        canvas.create_window((100*col, 50*row), window=buttons[col][row], anchor="nw")   


# Example connections
connections[0][0] = [[0,1],[1,1],[0,5],[1,2],[3,0],[3,1]]
connections[2][3] = [[3,3],[4,5],[2,1],[2,5]]

# Create and place arrows 
for col in range(col_tot):
    for row in range(row_tot):
        arrows[col][row] = []
        for connection in connections[col][row]:
            if col == connection[0] and row < connection[1]: # forward connection below
                arrows[col][row].append(canvas.create_line(col*100+40, row*50+16, connection[0]*100+40, connection[1]*50, arrow=LAST))
                circ_x = col*100+40
                circ_y = row*50+32+r
                canvas.create_oval(circ_x-r, circ_y-r, circ_x+r, circ_y+r)
            elif col == connection[0] and row > connection[1]: # forward connection above
                arrows[col][row].append(canvas.create_line(col*100+40, row*50+16, connection[0]*100+40, connection[1]*50+32, arrow=LAST))
                circ_x = col*100+40
                circ_y = row*50-r
                canvas.create_oval(circ_x-r, circ_y-r, circ_x+r, circ_y+r)
            elif row == connection[1] and col < connection[0]: # forward connection to the right
                arrows[col][row].append(canvas.create_line(col*100+40, row*50+16, connection[0]*100, connection[1]*50+16, arrow=LAST))
                circ_x = col*100+83+r
                circ_y = row*50+16
                canvas.create_oval(circ_x-r, circ_y-r, circ_x+r, circ_y+r)
            else:    
                if (col < connection[0]): # forward connection below to the right
                    arrows[col][row].append(canvas.create_line(col*100+40, row*50+16, connection[0]*100, connection[1]*50+16, arrow=LAST))
                    circ_x = col*100+40+(16+r)*((connection[0]-col)*100-40)/(50*(connection[1]-row))
                    circ_y = row*50+32+r
                    canvas.create_oval(circ_x-r, circ_y-r, circ_x+r, circ_y+r)

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