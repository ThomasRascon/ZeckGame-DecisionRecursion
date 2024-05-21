#include "ZeckGame.hpp"
#include <iostream>

using namespace std;

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


vector<vector<GameState*>>& ZeckGraph::getColumns() {
    return columns;
}


void ZeckGraph::createConnection(GameState* parent, const vector<char> childBins) {
    auto iter = gameMap.find(childBins);
    GameState* child;
    if(iter == gameMap.end()){
        int colIdx = size-numTokens(childBins);
        if(colIdx == columns.size()){
            columns.push_back(vector<GameState*>());
        }
        int rowIdx = columns[colIdx].size();
        child = new GameState(childBins, colIdx, rowIdx);
        columns[colIdx].push_back(child);
        gameMap.insert({childBins, child});
        stateQue.push(child);
    }
    else{
        child = iter->second;
    }
    parent->children.push_back(child->location);
    child->parents.push_back(parent->location);
}//EOF createConnection


int getK(int roof) {
    if(roof == 1){
        return 1;
    }
    return 2;
}


void ZeckGraph::makeMoves(GameState* parent, int roof) {
    //Split largest to smallest
    for(int i = parent->bins.size() - 2; i > 0; --i){
        int k = getK(roof);
        while(k <= roof && parent->bins[i] >= 2*k){
            const vector<char> childBins = split(parent->bins, i, k);
            createConnection(parent, childBins);
            ++k;
        }
    }

    //Combine largest to smallest
    for(int i = parent->bins.size() - 2; i > 0; --i){
        int k = getK(roof);
        while(k <= roof && parent->bins[i] >= k && parent->bins[i-1] >= k) {
            const vector<char> childBins = combine(parent->bins, i, k);
            createConnection(parent, childBins);
            ++k;
        }
    }

    //Combine 1's
    int k = getK(roof);
    while(k <= roof && parent->bins[0] >= 2*k && k <= stop){
        const vector<char> childBins = combine(parent->bins, 0, k);
        createConnection(parent, childBins);
        ++k;
    }
}//EOF makeMoves


bool ZeckGraph::build() {
    GameState* start = new GameState(size);
    gameMap.insert({start->bins, start});
    columns.push_back({start});
    stateQue.push(start);

    while(!stateQue.empty()){
        GameState* curr = stateQue.front();
        stateQue.pop();
        makeMoves(curr, 1);
    }

    for(const auto& p : gameMap){
        GameState* curr = p.second;
        makeMoves(curr, 10000);
    }

    return 1;
}//EOF build


ZeckGraph::~ZeckGraph(){
    for(const auto& pair : gameMap){
        delete pair.second;
    }
}//EOF destructor