//
// Created by Charlie Wang on 7/17/24.
//

#ifndef ZECKENDORFGAMES_MERGING_H
#define ZECKENDORFGAMES_MERGING_H
#include "ZeckGame.hpp"

class Merging {
    std::vector<std::vector<std::pair<GameState*, winningState>>> changeHistory;
    std::vector<std::pair<GameState*, int>> gameStates;

    static bool compareStates(const std::pair<GameState*, int> &x, const std::pair<GameState*, int> &y){
        if(x.second < y.second){
            return true;
        }
        return false;
    }

    Merging(){
        this->changeHistory = std::vector<std::vector<std::pair<GameState*, winningState>>>(0);
        this->gameStates = std::vector<std::pair<GameState*, int>>(0);
    }

    bool gameFinished(){
        return gameStates.size() == 0;
    }

    //returns true if a contradiction is found i.e. true for this specific n. false if not
    bool startGame(GameState* root){
        //construct the game tree
        this->changeHistory.emplace_back(makeGuess(root));
        if(changeHistory[0].size() == 0){
            return true;
        }

        while(changeHistory.size() != 0){
            GameState* nextGuess;
            nextGuess = selectNextGuess(root);
            if(nextGuess->status == Winning || nextGuess->status == Losing){
                return true;
            }
            this->changeHistory.emplace_back(makeGuess(nextGuess));
            while(changeHistory.back().size() == 0){
                changeHistory.resize(changeHistory.size() -1);
            }
            if(treeHasContradiction(root)){
                undo(changeHistory.back());
            }
        }

        return false;
    }

    GameState* selectNextGuess(GameState* root){
        std::sort(gameStates.begin(), gameStates.end(), compareStates);
        int count = 0;
        while(!gameStates.empty() && gameStates.begin()->second <= 0){
            ++count;
        }
        GameState* temp = (gameStates.begin()+count)->first;
        for(GameState* child: temp->children){
            if(child->status == Unknown){
                return child;
            }
        }

        for(GameState* parent: temp->parent){
            if(parent->status == Unknown){
                return parent;
            }
        }

        return temp;
    }

    //TODO
    std::vector<std::pair<GameState*, winningState>> makeGuess(GameState* root){
        if(root->status == Winning || root->status == Losing){
            return std::vector<std::pair<GameState*, winningState>>(0);;
        }
        root->status = Losing;

        if(anyConnectionLosing(root)){
            root->status = Winning;
            return std::vector<std::pair<GameState*, winningState>>(0);
        }

        std::vector<std::pair<GameState*, winningState>> history;
        history.emplace_back(std::pair<GameState*, winningState>(root, Unknown));

        for(GameState* child: root->children){
            history.emplace_back(std::pair(child, child->status));
            child->status = Winning;
        }
        for(GameState* parent: root->parents){
            history.emplace_back(std::pair(parent, parent->status));
            parent->status = Winning;
        }
        updateAllConnections(root);
        return history;
    }

    bool createsContradiction(GameState* root){
        if(root->status == Unknown){
            return false;
        }
        if(anyConnectionLosing(root)){
            if(root->status == Losing){
                return true;
            }
        }
        if(root->status == Winning && root->effectiveConnections == 0){
            return true;
        }
        return false;
    }

    //TODO
    //runs createsContradiction on the entire tree. should probably be implemented through ZeckGraph.
    bool treeHasContradiction(GameState* root){

    }

    bool anyConnectionLosing(GameState* root){
        for(GameState* child: root->children){
            if(child->status == Losing){
                return true;
            }
        }
        for(GameState* parent: root->parents){
            if(parent->status == Losing){
                return true;
            }
        }
        return false;
    }

    void undo(std::vector<std::pair<GameState*, winningState>> &history){
        for(auto state: history){
            state.first->status = state.second;
        }
        history[0].first->status = Winning;
    }

    //TODO
    //change it so it updates every single connection of the tree
    //probably should be implemented in ZeckGraph.
    void updateAllConnections(GameState* root){
        for(GameState* child: root->children){
            updateUncoloredConnections(child);
        }
        for(GameState* parent: root->parents){
            updateUncoloredConnections(parent);
        }
    }

    void updateUncoloredConnections(GameState* root){
        if(root->bins[0] < root->bins[1]) {
            root->effectiveConnections = -1;
            return;
        }
        int count = 0;
        for(GameState* connection: root->children){
            if(connection->status == Unknown){
                ++count;
            }
        }
        for(GameState* connection: root->parents){
            if(connection->status == Unknown){
                ++count;
            }
        }
        root->effectiveConnections = count;
    }
};


#endif //ZECKENDORFGAMES_MERGING_H
