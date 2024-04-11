#ifndef ZECK_GRAPH_HPP
#define ZECK_GRAPH_HPP

#include <unordered_map>
#include <functional>
#include <list>
#include <stack>
#include <queue>
#include <iostream>

using namespace std;


struct VectorCharHash {
    std::size_t operator()(const std::vector<char>& vec) const {
        std::size_t hash = 0;
        for (char c : vec) {
            hash = hash * 31 + c;
        }
        return hash;
    }
};//EOF VectorCharHash struct


struct GameState {
    const vector<char> bins;
    unsigned short int row;
    unsigned short int col;
    list<GameState*> children;
    list<GameState*> parents;


    /**
     * Constructor for the start state.
     * param: size The game size.
     */
    GameState(int size) : bins(createBins(size)) {} //EOF constructor


    /**
     * Override constructor for the non-start states.
     * param: bins The bins of the state to be constructed.
     */
    GameState(const vector<char>& bins) : bins(bins) {} //EOF override-constructor

    private:
        //Helper for start state constructor
        std::vector<char> createBins(int size) {
            std::vector<char> tempArray(numBins(size), 0);
            tempArray[0] = size;
            return tempArray;
        }//EOF creatBins


        //Helper for start state constructor
        int numBins(int size) {
            vector<int> FIBS = {1,2,3,5,8,13,21,34,55,89};
            int idx = 1;
            while (size >= FIBS[idx - 1]) {
                ++idx;
            }
            return idx - 1;
        }//EOF numBins
};//EOF GameState struct


typedef unordered_map<const vector<char>, GameState*, VectorCharHash> GameMap;
class ZeckGraph {
    private:
        GameMap gameMap;
        vector<vector<GameState*> > columns;
        queue<GameState*> stateQue;
        int size;
        int stop;

    public:
        /**
         * GameGraph constructor
         */
        ZeckGraph(int size, int stop);

        /**
         * GameGraph destructor
         */
        ~ZeckGraph();


        /**
         * Retrieves a constant reference to the columns of the Zeckendorf Graph.
         * return: A constant reference to a vector of pointers to GameState objects.
         */
        const vector<vector<GameState*>>* getColumns();


        /**
         * Connectes given game state to the game state passed as array.
         * param: parent The game state we are moving from.
         * param: childBins The bins of the child we are moving to.
         */
        void createConnection(GameState* parent, const vector<char> childBins);


        /**
         * Finds the moves that can be made fromt the given state.
         * param: parent The game state we are moving from.
         * param: roof The max number of moves of a type to be made.
         */
        void makeMoves(GameState* parent, int roof);

        /**
         * GameGraph constructor
         * param: n Number of starting tokens in the Zeckendorf Game.
         * param: cols how much columns to generate, -1 if you want all.
         * return: Wheather or not it built successfully
         */
        bool build();


        bool color();     
};

#endif /* ZECK_GRAPH_HPP */