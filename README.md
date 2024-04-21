#Zeck Game - Decision Recursion

#Overview
ZeckGame-DecisionRecursion is a project that implements the Zeckendorf Game using decision recursion. The Zeckendorf Game is a mathematical game where players take turns removing tokens from bins according to specific rules until no moves are possible. This project provides a graphical interface for visualizing the game state and exploring possible moves.

#Features
1. Display Move History: View move history, including colored highlights for specific moves. Export history to a text file if needed. Branch the history for guesses to track different move sequences.
2. Highlight Connections: Clicking a node highlights forward and backward connection edges and nodes, helping visualize the game's structure.
3. Generate with No Connections: Toggle between generating game states with or without connections displayed.
4. Interactive State Selection: Click on a state to select it, and click on a color button to assign a color to it.
5. Coloring Utility: Buttons for coloring all children and parents green without double-coloring.
6. Undo Functionality: Undo button to visually restore the previous state and delete it from the history.
7. Guess Distinguishing: Option to visually distinguish guesses from regular moves.

#Getting Started
Clone the repository to your local machine.
Compile the C++ library (clibrary.so) using the provided source code:

g++ -std=c++17 -shared -o clibrary.so -fPIC GraphStructure.cpp ZeckGame.cpp

Ensure you have Python and the necessary libraries installed (e.g., tkinter).
Run the Python script (main.py) to launch the graphical interface:

python GraphColoring.py

#Usage
Click on nodes to select them and perform actions like coloring or viewing connections.
Use the provided buttons to access different functionalities like coloring, toggling history, or undoing moves.
Scrollbars are available for navigating through larger game states.

#Contributing
Contributions are welcome! If you have ideas for improvements or new features, feel free to open an issue or submit a pull request.

#License
This project is licensed under the MIT License.
