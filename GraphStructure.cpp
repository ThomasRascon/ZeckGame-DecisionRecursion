#include "ZeckGame.hpp"

ZeckGraph* graph;
static GameMap gameMap = graph->getGameMap();
static unordered_map<pair<int,int>, GameState*> locMap = graph->getLocMap();
static GameMap::iterator iter = gameMap.begin();

extern "C" void build(int size, int stop) {
    graph = new ZeckGraph(size, stop);
    graph->build();
}

extern "C" list<pair<int,int>* getParents(int row, int col) {
    
}


extern "C" pair<int,int>* getChildren(int row, int col) {
    
}


extern "C" char* getBins() {
    
}


extern "C" pair<int,int> getLocation() {
    
}