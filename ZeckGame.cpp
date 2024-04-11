#include "ZeckGame.hpp"


int row = 0;
int col = 0;
int maxCol = 0;


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


const vector<vector<GameState*>>* ZeckGraph::getColumns() {
    return &columns;
}//EOF getColumns


void ZeckGraph::createConnection(GameState* parent, const vector<char> childBins) {
    auto iter = gameMap.find(childBins);
    GameState* child;
    if(iter == gameMap.end()){
        child = new GameState(childBins);
        gameMap.insert(make_pair(childBins, child));
        int colIdx = size-numTokens(childBins);
        if(colIdx == columns.size()){
            columns.push_back(vector<GameState*>());
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
    while(k <= roof && parent->bins[0] >= 2*k && k <= stop){
        const vector<char> childBins = combine(parent->bins, 0, k);
        createConnection(parent, childBins);
        ++k;
    }
}//EOF makeMoves


bool ZeckGraph::build() {
    GameState* start = new GameState(size);
    columns.push_back({start});
    stateQue.push(start);
    stateQue.push(nullptr);

    while(!stateQue.empty()){
        GameState* curr = stateQue.front();
        stateQue.pop();
        if(curr == nullptr){
            if(col > maxCol){
                maxCol = col;
            }
            row += 1;
            col = 0;
            stateQue.push(nullptr);
        }
        else{
            col += 1;
            makeMoves(curr, 1);
        }
    }

    for(const auto& col : columns){
        for(const auto curr : col){
            makeMoves(curr, numeric_limits<float>::infinity());
        }
    }

    // int colIdx = 0;
    // for(const auto& col : columns){
    //     cout << "Column " << colIdx << ":" << endl;
    //     for(const auto curr : col){
    //         cout << "\t";
    //         for(int i = curr->bins.size()-1; i >= 0; --i){
    //             cout << static_cast<int>(curr->bins[i]) << ",";
    //         }
    //         cout << endl;
    //         //cout << "\t" << curr->parents.size() << endl;
    //         for(const auto child : curr->children){
    //             cout << "\t\t";
    //             for(int i = child->bins.size()-1; i >= 0; --i){
    //                 cout << static_cast<int>(child->bins[i]) << ",";
    //             }
    //             cout << endl;
    //         }
    //     }
    //     colIdx++;
    // }

    return 1;
}//EOF build


ZeckGraph::~ZeckGraph(){
    for(const auto pair : gameMap){
        delete pair.second;
    }
}//EOF destructor