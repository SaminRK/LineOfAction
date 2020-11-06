#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include <cstdio>
#include <cstdlib>
#include "core_ai.cpp"
using namespace std;

int main (int argc, char * argv[]) {

    char my_color = argv[1][0];
    int arena_size = atoi(argv[2]);

    core_ai bot(my_color, 6, arena_size);

    string cmd;

    while (true) {
    	cin >> cmd;
    	cerr << cmd << endl;
    	if (cmd == "move") {
    		bot.get_map();
    		bot.make_move();
    	} else if (cmd == "close") {
    		break;
    	}
        
    }
    return 0;
}
