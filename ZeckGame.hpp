#ifndef ZECK_GRAPH_HPP
#define ZECK_GRAPH_HPP

#include <unordered_map>
#include <functional>
#include <queue>


struct Pair {
    int col;
    int row;
};//EOF Pair struct


struct PairVector {
    Pair* data;
    size_t size;
};//EOF PairVector struct


struct CharVector {
    const char* data;
    size_t size;
    Pair location;
};//EOF CharVector struct


struct VectorHash {
    template <typename T>
    size_t operator()(const std::vector<T>& vec) const {
        size_t hashValue = 0;
        for (const T& element : vec) {
            hashValue = hashValue * 31 + std::hash<T>()(element);
        }
        return hashValue;
    }
};//EOF VectorHash struct


struct GameState {
    const std::vector<char> bins;
    const Pair location;
    std::vector<Pair> children;
    std::vector<Pair> parents;


    /**
     * Constructor for the start state.
     * param: size The game size.
     */
    GameState(int size) : bins(createBins(size)), location(Pair{0,0}){} //EOF constructor


    /**
     * Override constructor for the non-start states.
     * param: bins The bins of the state to be constructed.
     */
    GameState(const std::vector<char>& bins, int col, int row) :
        bins(bins), location(Pair{col,row}) {} //EOF override-constructor

    private:
        //Helper for start state constructor
        std::vector<char> createBins(int size) {
            std::vector<char> tempArray(numBins(size), 0);
            tempArray[0] = size;
            return tempArray;
        }//EOF creatBins


        //Helper for start state constructor
        int numBins(int size) {
            std::vector<int> FIBS = {1,2,3,5,8,13,21,34,55,89};
            int idx = 1;
            while (size >= FIBS[idx - 1]) {
                ++idx;
            }
            return idx - 1;
        }//EOF numBins
};//EOF GameState struct


typedef std::unordered_map<const std::vector<char>, GameState*, VectorHash> GameMap;
typedef std::unordered_map<std::vector<int>, GameState*, VectorHash> LocationMap;
class ZeckGraph {
    private:
        GameMap gameMap;
        std::vector<std::vector<GameState*>> columns;
        std::queue<GameState*> stateQue;
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
         * Connectes given game state to the game state passed as array.
         * param: parent The game state we are moving from.
         * param: childBins The bins of the child we are moving to.
         */
        void createConnection(GameState* parent, const std::vector<char> childBins);


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


        std::vector<std::vector<GameState*>>& getColumns();         
};

#endif /* ZECK_GRAPH_HPP */