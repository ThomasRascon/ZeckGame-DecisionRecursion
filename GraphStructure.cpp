#include "ZeckGame.hpp"
#include <cstdio>
#include <iostream>

using namespace std;
             
static int curr_row = 0;
static int curr_col = 0;
static ZeckGraph* graph = nullptr;
static vector<vector<GameState*>> columns; 


extern "C" void build(int size, int stop) {
    graph = new ZeckGraph(11, numeric_limits<float>::infinity());
    graph->build();
    columns = graph->getColumns();
}//EOF build


extern "C" void printGraph() {
}


extern "C" PairVector getParents(int row, int col) {
    if(col < 0 || row < 0 || col >= columns.size() || row >= columns[col].size()){
        printf("Did not find location.");
        exit(1);
    }
    GameState* state = columns[col][row];
    return PairVector{state->parents.data(), state->parents.size()};
}//EOF getParents


extern "C" PairVector getChildren(int row, int col) {
    if(col < 0 || row < 0 || col >= columns.size() || row >= columns[col].size()){
        printf("Did not find location.");
        exit(1);
    }
    GameState* state = columns[col][row];
    return PairVector{state->children.data(), state->children.size()};
}//EOF getChildren


extern "C" CharVector getBins() {
    GameState* curr = columns[curr_col][curr_row];
    return CharVector{curr->bins.data(), curr->bins.size()};
}//EOF getBins


extern "C" Pair getLocation() {
    GameState* curr = columns[curr_col][curr_row];
    curr_row += 1;
    if(curr_row == columns[curr_col].size()){
        curr_col += 1;
        curr_row = 0;
    }
    return curr->location;
}//EOF getLocation


void deallocate() {
    delete graph;
}//EOF deallocate