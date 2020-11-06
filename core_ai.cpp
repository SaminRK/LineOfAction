#include <iostream>
#include <queue>
#include <vector>
#include <cstring>
#include <algorithm>
using namespace std;

const int INF = 1e9;

class core_ai {
	char my_color;
	char opp_color;
	vector<string> game_grid;
	int search_depth;
	int ARENA_SIZE;
	pair<pair<int,int>, pair<int,int> > optimal_move;

	int di[8] = {0, 1, 1,  1,  0, -1, -1, -1};
	int dj[8] = {1, 1, 0, -1, -1, -1,  0,  1};

	int alpha_beta(int depth, int alpha, int beta, bool maximizing_player, vector<string> grid);
	int static_evaluation(const vector<string> & grid);
	pair<pair<int,int>, pair<int,int> > get_first_move();
	bool check_win(char color, const vector<string> & grid);
	vector<pair<pair<int,int>, pair<int,int> > > get_valid_moves(char my_color, vector<string> grid);
	vector<pair<int, pair<int, vector<string> > > > rearrange_moves_by_cost(vector<pair<pair<int,int>, pair<int,int> > > valid_moves, vector<string> grid);
	void print_grid(const vector<string> & grid);

public:
	core_ai(char my_color, int search_depth, int arena_size);
	void get_map();
	void make_move();
};

core_ai::core_ai(char my_color, int search_depth, int arena_size) {
	this->my_color = my_color;
	if (my_color == 'B') opp_color = 'W';
	else opp_color = 'B';
	this->search_depth = search_depth;
	this->ARENA_SIZE = arena_size;

	cerr << "AI started" << endl;

	game_grid.resize(ARENA_SIZE);
}

void core_ai::get_map() {
	for (int i = 0; i < ARENA_SIZE; ++i) {
		cin >> game_grid[i];
	}
	print_grid(game_grid);
}

void core_ai::print_grid(const vector<string> & grid) {
	for (int i = 0; i < ARENA_SIZE; ++i) {
		for (int j = 0; j < ARENA_SIZE; ++j) {
			fprintf(stderr, "%c", grid[i][j]);
		}
		fprintf(stderr, "\n");
	}
}

bool core_ai::check_win(char color, const vector<string> & grid) {
	// printf("started checking winner\n");
	queue<pair<int,int> > q;
	int connected_gutis = 0;
	bool vis[ARENA_SIZE][ARENA_SIZE];
	memset(vis, false, sizeof vis);

	for (int i = 0; i < ARENA_SIZE; ++i) {
		for (int j = 0; j < ARENA_SIZE; ++j) {
			if (grid[i][j] == color) {
				q.push({i,j});
				++connected_gutis;
				vis[i][j] = true;
				i = ARENA_SIZE;
				break;
			}
		}
	}
	
	while (!q.empty()) {
		auto p = q.front(); q.pop();
		int i = p.first, j = p.second;
		for (int l = 0; l < 8; ++l) {
			int ni = i + di[l], nj = j + dj[l];
			if (ni >= 0 && ni < ARENA_SIZE && nj >= 0 && nj < ARENA_SIZE &&
				!vis[ni][nj] && grid[ni][nj] == color) {
				q.push({ni, nj});
				++connected_gutis;
				vis[ni][nj] = true;
			}
		}
	}

	int gutis = 0;
	for (int i = 0; i < ARENA_SIZE; ++i) {
		for (int j = 0; j < ARENA_SIZE; ++j) {
			if (grid[i][j] == color) ++gutis;
		}
	}
	// printf("done checking winner connected_gutis: %d total gutis %d\n", connected_gutis, gutis);
	return connected_gutis == gutis;
}

int core_ai::static_evaluation(const vector<string> & grid) {
	int pieceSquareTable[8][8] = {
		{-80, -25, -20, -20, -20, -20, -25, -80},
		{-25,  10,  10,  10,  10,  10,  10,  -25},
		{-20,  10,  25,  25,  25,  25,  10,  -20},
		{-20,  10,  25,  50,  50,  25,  10,  -20},
		{-20,  10,  25,  50,  50,  25,  10,  -20},
		{-20,  10,  25,  25,  25,  25,  10,  -20},
		{-25,  10,  10,  10,  10,  10,  10,  -25}, 
		{-80, -25, -20, -20, -20, -20, -25, -80}
	};

	int value = 0;

	for (int i = 0; i < ARENA_SIZE; ++i) {
		for (int j = 0; j < ARENA_SIZE; ++j) {
			if (grid[i][j] == my_color) value += pieceSquareTable[i][j];
			else if (grid[i][j] == opp_color) value -= pieceSquareTable[i][j];
		}
	}

	return value;
}

vector<pair<pair<int,int>, pair<int,int> > > core_ai::get_valid_moves(char color, vector<string> grid) {
	vector<pair<pair<int,int>, pair<int,int> > > valid_moves;
	
	for (int i = 0; i < ARENA_SIZE; ++i) {
		for (int j = 0; j < ARENA_SIZE; ++j) {
			if (grid[i][j] == color) {
				//fprintf(stderr, "(%d, %d)\n", i, j);
				for (int l = 0; l < 8; ++l) {
					int gutis = 1;

					for (int m = 1; m < ARENA_SIZE; ++m) {
						int ni = i + m * di[l], nj = j + m * dj[l];
						if (ni >= 0 && ni < ARENA_SIZE && nj >= 0 && nj < ARENA_SIZE) {
							if (grid[ni][nj] != '.')
								++gutis;
						} else {
							break;
						}
					}
					for (int m = 1; m < ARENA_SIZE; ++m) {
						int ni = i - m * di[l], nj = j - m * dj[l];
						if (ni >= 0 && ni < ARENA_SIZE && nj >= 0 && nj < ARENA_SIZE) {
							if (grid[ni][nj] != '.')
								++gutis;
						} else {
							break;
						}
					}
					
					int ti = i + gutis * di[l], tj = j + gutis * dj[l];
					if (ti >= 0 && ti < ARENA_SIZE && tj >= 0 && tj < ARENA_SIZE &&
						grid[ti][tj] != color) {

						bool possible = true;

						for (int m = 1; m < gutis; ++m) {
							int ni = i + m * di[l], nj = j + m * dj[l];
							if (grid[ni][nj] != '.' && grid[ni][nj] != color) { // opponent
								possible = false;
								break;
							}
						}

						if (possible) {
							// fprintf(stderr, "->(%d, %d)\n", ti, tj);
							valid_moves.push_back({{i, j}, {ti, tj}});
						}
					}
				}
			}
		}
	}

	return valid_moves;
}

vector<pair<int, pair<int, vector<string> > > > core_ai::rearrange_moves_by_cost(vector<pair<pair<int,int>, pair<int,int> > > valid_moves, vector<string> grid) {
	vector<pair<int, pair<int, vector<string> > > > rearranged_cost_of_move((int)valid_moves.size());

	for (int i = 0; i < (int)valid_moves.size(); ++i) {
		vector<string> new_grid(grid);
		pair<int,int> target = valid_moves[i].second;
		pair<int,int> source = valid_moves[i].first;
		new_grid[target.first][target.second] = new_grid[source.first][source.second];
		new_grid[source.first][source.second] = '.';
		int cost = static_evaluation(new_grid);

		rearranged_cost_of_move[i] = {cost, {i, new_grid}};

	}

	sort(rearranged_cost_of_move.begin(), rearranged_cost_of_move.end());

	return rearranged_cost_of_move;
}

int core_ai::alpha_beta(int depth, int alpha, int beta, bool maximizing_player, vector<string> grid) {

	if (check_win(my_color, grid)) {
		return INF;
	}
	if (check_win(opp_color, grid)) {
		return -INF;
	}
	if (depth == 0) {
		return static_evaluation(grid);
	}

	if (maximizing_player) {
		int value = -INF;

		vector<pair<pair<int,int>, pair<int,int> > > valid_moves = get_valid_moves(my_color, grid);
		vector<pair<int, pair<int, vector<string> > > > rearranged_cost_of_move = rearrange_moves_by_cost(valid_moves, grid); // (cost, (move_index, grid))

		for (int i = (int)rearranged_cost_of_move.size() - 1; i >= 0; --i) {
			int cost = rearranged_cost_of_move[i].first;
			pair<pair<int,int>, pair<int,int> > move = valid_moves[rearranged_cost_of_move[i].second.first];
			vector<string> child_grid = rearranged_cost_of_move[i].second.second;

			int child_val = alpha_beta(depth-1, alpha, beta, false, child_grid);
			
			if (child_val > value) {
				value = child_val;
				if (depth == search_depth) {
					optimal_move = move; 
				}
			}
			alpha = max(alpha, value);
			if (alpha >= beta) break;
		}
		return value;
	} else {
		int value = INF;

		vector<pair<pair<int,int>, pair<int,int> > > valid_moves = get_valid_moves(opp_color, grid);
		vector<pair<int, pair<int, vector<string> > > > rearranged_cost_of_move = rearrange_moves_by_cost(valid_moves, grid); // (cost, (move_index, grid))

		for (int i = 0; i < (int)rearranged_cost_of_move.size(); ++i) {
			int cost = rearranged_cost_of_move[i].first;
			pair<pair<int,int>, pair<int,int> > move = valid_moves[rearranged_cost_of_move[i].second.first];
			vector<string> child_grid = rearranged_cost_of_move[i].second.second;

			int child_val = alpha_beta(depth-1, alpha, beta, true, child_grid);

			value = min(value, child_val);
			beta = min(beta, value);

			if (beta <= alpha) break;
		}
		return value;
	}
}


void core_ai::make_move() {
	optimal_move = get_first_move();
	int result = alpha_beta(search_depth, -INF, +INF, true, game_grid);

	fprintf(stderr, "result=%d\n", result);

	cout << optimal_move.first.second << " " << optimal_move.first.first <<
	" " << optimal_move.second.second << " " << optimal_move.second.first << endl;
}

pair<pair<int,int>, pair<int,int> > core_ai::get_first_move() {
	cerr << "making move" << endl;
	for (int i = 0; i < ARENA_SIZE; ++i) {
		for (int j = 0; j < ARENA_SIZE; ++j) {
			if (game_grid[i][j] == my_color) {
				for (int dir = 0; dir < 8; ++dir) {
					int count = 1;

					for (int d = 1; d <= ARENA_SIZE; ++d) {
						int ni = i+d*di[dir], nj = j+d*dj[dir];
						if (ni >= 0 && ni < ARENA_SIZE && nj >= 0 && nj < ARENA_SIZE) {
							if (game_grid[ni][nj] != '.') {
								++count;
							}
						} else break;
					}
					for (int d = 1; d <= ARENA_SIZE; ++d) {
						int ni = i-d*di[dir], nj = j-d*dj[dir];
						if (ni >= 0 && ni < ARENA_SIZE && nj >= 0 && nj < ARENA_SIZE) {
							if (game_grid[ni][nj] != '.') {
								++count;
							}
						} else break;
					}

					int ti = i+count*di[dir], tj = j+count*dj[dir];
					if (ti < 0 || ti >= ARENA_SIZE || tj < 0 || tj >= ARENA_SIZE || game_grid[ti][tj] == my_color) {
						continue;
					}

					bool possible = true;
					for (int d = 1; d < count; ++d) {
						int ni = i+d*di[dir], nj = j+d*dj[dir];
						if (ni < 0 || ni >= ARENA_SIZE || nj < 0 || nj >= ARENA_SIZE || game_grid[ni][nj] == opp_color) {
							possible = false;
							break;
						}
					}

					if (possible) {
						// cerr << j << " " << i << " " << j + count*dj[dir]  << " " << i + count*di[dir] << endl;
						// cout << j << " " << i << " " << j + count*dj[dir]  << " " << i + count*di[dir] << endl;
						return {{i, j}, {i + count*di[dir], j + count*dj[dir]}};
					}
				}
			}
		}
	}
}

	// function alphabeta(node, depth, α, β, maximizingPlayer) is
 //    if depth = 0 or node is a terminal node then
 //        return the heuristic value of node
 //    if maximizingPlayer then
 //        value := −∞
 //        for each child of node do
 //            value := max(value, alphabeta(child, depth − 1, α, β, FALSE))
 //            α := max(α, value)
 //            if α ≥ β then
 //                break (* β cutoff *)
 //        return value
 //    else
 //        value := +∞
 //        for each child of node do
 //            value := min(value, alphabeta(child, depth − 1, α, β, TRUE))
 //            β := min(β, value)
 //            if β ≤ α then
 //                break (* α cutoff *)
 //        return value
