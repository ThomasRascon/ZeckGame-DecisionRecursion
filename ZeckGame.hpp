#ifndef ZECK_GRAPH_HPP
#define ZECK_GRAPH_HPP

#include <unordered_map>
#include <list>
#include <stack>

using namespace std;

//Declare array of Fibonacci numbers.
const vector<int> FIBS = {1,2,3,5,8,13,21,34,55,89};
int largestBin(int size) {
    int idx = 1;
    while(size >= FIBS[idx-1]){
        ++idx;
    }
    return idx-1;
}//EOF largestBin


struct GameState {
    vector<char> bins;
    stack<char> type;
    stack<char> unvisted_links;
    bool hasPurple;
    char col;
    list<GameState*> children;
    list<GameState*> parents;

    /**
     * Constructor for the start state
     * param: size The game size
     */
    GameState(int size) : bins(size){
        fill(bins.begin(), bins.end(), 0);
        bins[0] = size;
    }//EOF constructor
};//EOF GameState struct

class ZeckGraph {
    private:
        unordered_map<double, GameState*> gameMap;
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
         * Finds the moves that can be made from the given state.
         * param: parent The game state we are moving from.
         */
        void createConnection(GameState*& parent);


        /**
         * Finds the moves that can be made fromt the given state.
         * param: parent The game state we are moving from.
         */
        void makeMoves(GameState*& parent);

        /**
         * GameGraph constructor
         * param: n Number of starting tokens in the Zeckendorf Game.
         * param: cols how much columns to generate, -1 if you want all.
         * return: Wheather or not it built successfully
         */
        bool build();       
}

#endif /* ZECK_GRAPH_HPP */
