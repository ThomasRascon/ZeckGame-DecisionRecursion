#include "ZeckGame.hpp"
#include <queue>

ZeckGraph::ZeckGraph(int size, int stop) : size(size), stop(stop){

}//EOF constructor


void ZeckGraph::makeMoves(GameState*& parent) {
    //Split largest first
    for(int i = parent->bins.size(); i >= 1; --i){
        int k = 1;
        while(parent->bins[i] >= 2*k){
            vector<char> childBins = split(parent->bins, i, k);
            addChild(parent, childBins);
        }
    }
    
    //Combine largest second
    for(int i = parent->bins.size(); i >= 1; --i){
        int k = 1;
        while(parent->bins[i] >= k && parent->bins[i-1] >= k) {
            vector<char> childBins = combine(parent->bins, i, k);
            addChild(parent, childBins);
        }
    }
    
    //Combine 1's third
    for(int i = parent->bins.size(); i >= 0; --i){
        int k = 1;
        while(parent->bins[i] >= 2*k && k < stop){
            vector<char> childBins = combine(parent->bins, i, k);
            addChild(parent, childBins);
        }
    }
}//EOF makeMoves


bool ZeckGraph::build() {
    queue<GameState*> q;
    GameState* start = new GameState(size);
    q.push(start);

    while(!q.empty()){
        GameState* curr = q.front();
        q.pop();
        makeMoves(curr);
    }
}//EOF build


ZeckGraph::~ZeckGraph(){

}//EOF destructor
