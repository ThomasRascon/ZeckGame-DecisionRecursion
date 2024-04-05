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

def selectedLambda(row, col):
    return lambda: buttonClicked(row, col)

def giveColorLambda(color):
    return lambda: giveColor(color)

def buttonClicked(n, m):
    print("Button (", n, ", ", m, ") clicked")

    for button_list in buttons:
        for button in button_list:
            if button["bg"] == "light pink":
                button.configure(bg="light blue") 

    buttons[n][m].configure(bg="light pink")

def giveColor(color):
    for button_list in buttons:
        for button in button_list:
            if button["bg"] == "light pink":
                button.configure(bg=color) 

def toggleText():
    for button_list in buttons:
        for button in button_list:
            if button["bg"] == "light pink":
                if button["fg"] == "brown":
                    button.configure(fg="black") 
                else: 
                    button.configure(fg="brown")
                
                
    


col_tot = 4
row_tot = 8

buttons = [[None]*row_tot for i in range(col_tot)]
borders = [[None]*row_tot for i in range(col_tot)]
root = Tk() 
root.geometry("900x600")
root.configure(background="dark grey")

for col in range(col_tot):
    for row in range (row_tot):
        
        buttons[col][row] = Button(root, text = "button "+ str(col) + ", " + str(row), 
                                  command = selectedLambda(col, row), 
                                  bg="light blue", activebackground="grey", bd = 0)
        buttons[col][row].place(x=400+100*col, y=200+50*row)

        

colorGreen = Button(root, text = "Color Green", 
                    command = giveColorLambda("lime"), 
                    bg="lime", activebackground="grey", bd=0)
colorPurple = Button(root, text = "Color purple", 
                    command = giveColorLambda("fuchsia"), 
                    bg="fuchsia", activebackground="grey", bd=0)
textToggler = Button(root, text = "Toggle Text Color", 
                    command = toggleText, 
                    bg="White", activebackground="grey", bd=0)

colorGreen.place(x=50, y=450)
colorPurple.place(x=50, y=400)
textToggler.place(x=50, y=350)

root.mainloop()

