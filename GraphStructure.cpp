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


extern "C" PairVector getParents(int col, int row) {
    if(col < 0 || row < 0 || col >= columns.size() || row >= columns[col].size()){
        printf("Did not find location.");
        exit(1);
    }
    GameState* state = columns[col][row];
    return PairVector{state->parents.data(), state->parents.size()};
}//EOF getParents


extern "C" PairVector getChildren(int col, int row) {
    if(col < 0 || row < 0 || col >= columns.size() || row >= columns[col].size()){
        printf("Did not find location.");
        exit(1);
    }
    GameState* state = columns[col][row];
    return PairVector{state->children.data(), state->children.size()};
}//EOF getChildren


extern "C" int columnHeight(int colIdx) {
    return columns[colIdx].size();
}//EOF columnHeight


extern "C" bool moreStates() {
    return curr_col < columns.size();
}//EOF moreStates


extern "C" CharVector getState() {
    GameState* curr = columns[curr_col][curr_row];
    curr_row += 1;
    if(curr_row == columns[curr_col].size()){
        curr_col += 1;
        curr_row = 0;
    }
    return CharVector{curr->bins.data(), curr->bins.size(), curr->location};
}//EOF getState


extern "C" void deallocate() {
    delete graph;
}//EOF deallocate