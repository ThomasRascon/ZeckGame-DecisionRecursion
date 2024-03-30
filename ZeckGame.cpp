#include "ZeckGame.hpp"


vector<char> split(vector<char> bins, int i, int k) {
    bins[i] -= 2*k;
    bins[i+1] += k;
    if(i==1){
        bins[0] += k;
    }
    else{
        bins[i-2] += k;
    }
    return bins;
}//EOF split


vector<char> combine(vector<char> bins, int i, int k) {
    if(i==0){
        bins[0] -= 2*k;
    }
    else{
        bins[i] -= k;
        bins[i-1] -= k;
    }
    bins[i+1] += k;
    return bins;
}//EOF combine


int numTokens(vector<char> bins) {
    int sum = 0;
    for(auto num : bins){
        sum += num;
    }
    return sum;
}//EOF nonTokens


ZeckGraph::ZeckGraph(int size, int stop) : size(size), stop(stop) {} //EOF constructor


void ZeckGraph::createConnection(GameState* parent, const vector<char> childBins) {
    auto iter = gameMap.find(childBins);
    GameState* child;
    if(iter == gameMap.end()){
        child = new GameState(childBins);
        gameMap.insert({childBins, child});
        int colIdx = size-numTokens(childBins);
        if(colIdx == columns.size()){
            columns.push_back({});
        }
        columns[colIdx].push_back(child);
        stateQue.push(child);
    }
    else{
        child = iter->second;
    }
    parent->children.push_back(child);
    child->parents.push_back(parent);
}//EOF createConnection


void ZeckGraph::makeMoves(GameState* parent, int roof) {
    //Split largest first
    for(int i = parent->bins.size() - 2; i > 0; --i){
        int k = 1;
        while(k <= roof && parent->bins[i] >= 2*k){
            const vector<char> childBins = split(parent->bins, i, k);
            createConnection(parent, childBins);
            ++k;
        }
    }
    
    //Combine largest second
    for(int i = parent->bins.size() - 2; i > 0; --i){
        int k = 1;
        while(k <= roof && parent->bins[i] >= k && parent->bins[i-1] >= k) {
            const vector<char> childBins = combine(parent->bins, i, k);
            createConnection(parent, childBins);
            ++k;
        }
    }
    
    //Combine 1's third
    int k = 1;
    while(parent->bins[0] >= 2*k && k <= stop){
        const vector<char> childBins = combine(parent->bins, 0, k);
        createConnection(parent, childBins);
        ++k;
    }
}//EOF makeMoves


bool ZeckGraph::build() {
    GameState* start = new GameState(size);
    stateQue.push(start);

    while(!stateQue.empty()){
        GameState* curr = stateQue.front();
        stateQue.pop();
        makeMoves(curr, 1);
    }

    for(const auto& col : columns){
        for(const auto curr : col){
            makeMoves(curr, float('inf'));
        }
    }
}//EOF build


ZeckGraph::~ZeckGraph(){
    for(const auto pair : gameMap){
        delete pair.second;
    }
}//EOF destructor