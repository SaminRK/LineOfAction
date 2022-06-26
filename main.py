import pygame_menu
import sys
import subprocess
import threading
from draw import *
from pygame.locals import *


class LineOfAction:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.event.set_allowed([QUIT, MOUSEBUTTONUP])
        pygame.event.set_blocked(MOUSEMOTION)

        pygame.display.set_caption("Line of Action")
        self.screen = pygame.display.set_mode((600, 400))

        self.box_size = 40
        self.guti_radius = 16
        self.turn = "W"  # B = black's turn; W = white's turn
        self.arena_size = 8
        self.valid_moves = []
        self.source = None  # marks selected tile by human user for making move
        self.board = None
        self.dx = [0, 1, 1, 1, 0, -1, -1, -1]
        self.dy = [1, 1, 0, -1, -1, -1, 0, 1]
        self.player_white = 0
        self.player_black = 0
        self.board_written = False
        self.humans_turn = False

        self.drawer = Draw(self.screen, self.box_size, self.guti_radius)

        self.menu = pygame_menu.Menu(350, 400, "Line of Action")
        self.menu.add_selector(
            "Black: ",
            [
                ("HUMAN", 0),
                ("MACHINE-T", 1),
                ("MACHINE-Q", 2),
                ("MACHINE-A", 3),
                ("MACHINE-AT", 4),
            ],
            onchange=self.set_player_black,
        )
        self.menu.add_selector(
            "White: ",
            [
                ("HUMAN", 0),
                ("MACHINE-T", 1),
                ("MACHINE-Q", 2),
                ("MACHINE-A", 3),
                ("MACHINE-AT", 4),
            ],
            onchange=self.set_player_white,
        )
        self.menu.add_selector(
            "Arena Size: ", [("8*8", 0), ("6*6", 1)], onchange=self.set_arena_size
        )
        self.menu.add_button("PLAY", self.start_game)
        self.menu.add_button("QUIT", pygame_menu.events.EXIT)

        self.main_menu = True

        # ai
        self.machine_white = None
        self.machine_black = None

    def game_setup(self):
        self.turn = "W"  # B = black's turn; W = white's turn
        self.valid_moves = []
        self.source = None
        self.board = self.make_board(self.arena_size)

        # initiate AIs
        if self.player_white != 0:
            print("white is ai")
            self.machine_white = subprocess.Popen(
                [
                    "./ai",
                    "W",
                    str(self.arena_size),
                    self.index_to_heuristic_code(self.player_white),
                ],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,
            )
        else:
            print("white is human")

        if self.player_black != 0:
            print("black is ai")
            self.machine_black = subprocess.Popen(
                [
                    "./ai",
                    "B",
                    str(self.arena_size),
                    self.index_to_heuristic_code(self.player_black),
                ],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,
            )
        else:
            print("black is human")

        self.setup_next_player()

    def index_to_heuristic_code(self, index):
        if index == 1:
            heuristic = "T"
        elif index == 2:
            heuristic = "Q"
        elif index == 3:
            heuristic = "A"
        else:
            heuristic = "B"

        return heuristic

    def make_board(self, size):
        board = None
        if size == 8:
            board = [
                [" ", "B", "B", "B", "B", "B", "B", " "],
                ["W", " ", " ", " ", " ", " ", " ", "W"],
                ["W", " ", " ", " ", " ", " ", " ", "W"],
                ["W", " ", " ", " ", " ", " ", " ", "W"],
                ["W", " ", " ", " ", " ", " ", " ", "W"],
                ["W", " ", " ", " ", " ", " ", " ", "W"],
                ["W", " ", " ", " ", " ", " ", " ", "W"],
                [" ", "B", "B", "B", "B", "B", "B", " "],
            ]
        elif size == 6:
            board = [
                [" ", "B", "B", "B", "B", " "],
                ["W", " ", " ", " ", " ", "W"],
                ["W", " ", " ", " ", " ", "W"],
                ["W", " ", " ", " ", " ", "W"],
                ["W", " ", " ", " ", " ", "W"],
                [" ", "B", "B", "B", "B", " "],
            ]
        return board

    def handle_ai(self, machine, color):
        if not machine:
            return
        brd = self.board_string()
        print(brd, file=machine.stdin, flush=True, end="")
        move = machine.stdout.readline().strip("\n").split(" ")
        source = (int(move[0]), int(move[1]))
        target = (int(move[2]), int(move[3]))
        valid = self.check_valid_move(source, target, color)  # make source target pairs
        if valid:
            self.make_move(source, target)
            winner = self.check_win_both(target)
            if (
                not winner and not self.main_menu
            ):  # if user has not already gone to the main menu
                self.setup_next_player()
            else:
                self.drawer.draw_win(self.board, self.arena_size, winner)
        else:
            raise Exception("AI ", machine, color, " has given invalid move ", move)

    def check_valid_move(self, source, target, color):
        if self.board[source[1]][source[0]] != color:
            print("source tile does not have correct guti")
            return False

        if (
            target[0] < 0
            or target[0] >= self.arena_size
            or target[1] < 0
            or target[1] >= self.arena_size
        ):
            print("target out of board")
            return False

        if self.board[target[1]][target[0]] == color:
            print("cannot land on own piece")
            return False

        direction = -1

        #            0  1  2   3   4   5   6   7
        # self.dx = [0, 1, 1,  1,  0, -1, -1, -1]
        # self.dy = [1, 1, 0, -1, -1, -1,  0,  1]

        if source[0] == target[0]:
            if source[1] > target[1]:
                direction = 4
            elif source[1] < target[1]:
                direction = 0
        elif source[1] == target[1]:
            if source[0] > target[0]:
                direction = 6
            elif source[0] < target[0]:
                direction = 2
        elif source[0] - target[0] == source[1] - target[1]:
            if source[0] < target[0]:
                direction = 1
            elif source[0] > target[0]:
                direction = 5
        elif source[0] - target[0] == target[1] - source[1]:
            if source[0] < target[0]:
                direction = 3
            elif source[0] > target[0]:
                direction = 7

        if direction == -1:
            print("source and target are not on a line")
            return False

        count = 1
        for moves in range(self.arena_size):  # make this a method
            x = source[0] + (moves + 1) * self.dx[direction]
            y = source[1] + (moves + 1) * self.dy[direction]
            if 0 <= x < self.arena_size and 0 <= y < self.arena_size:
                if self.board[y][x] != " ":
                    count += 1
            else:
                break
        for moves in range(self.arena_size):
            x = source[0] - (moves + 1) * self.dx[direction]
            y = source[1] - (moves + 1) * self.dy[direction]
            if 0 <= x < self.arena_size and 0 <= y < self.arena_size:
                if self.board[y][x] != " ":
                    count += 1
            else:
                break
        return max(abs(source[0] - target[0]), abs(source[1] - target[1])) == count

    def setup_next_player(self):
        if self.turn == "B":
            self.turn = "W"
        else:
            self.turn = "B"

        print("next turn is from: ", self.turn)

        if self.turn == "B":
            if self.player_black == 0:
                self.humans_turn = True
            else:
                self.humans_turn = False
        else:
            if self.player_white == 0:
                self.humans_turn = True
            else:
                self.humans_turn = False

        if self.humans_turn:
            print("move will be made by human")
        else:
            print("move will be made by machine")

        self.drawer.redraw(self.board, self.arena_size, self.turn)
        self.drawer.update()

        if not self.humans_turn:
            if self.turn == "B":
                ai_handler = threading.Thread(
                    target=self.handle_ai,
                    args=(
                        self.machine_black,
                        "B",
                    ),
                )
            else:
                ai_handler = threading.Thread(
                    target=self.handle_ai,
                    args=(
                        self.machine_white,
                        "W",
                    ),
                )
            ai_handler.start()

    def handle_click_box(self, click_position):
        box_index = (
            int(click_position[0] / self.box_size),
            int(click_position[1] / self.box_size),
        )
        marker_position = (
            int(box_index[0] * self.box_size + self.box_size / 2),
            int(box_index[1] * self.box_size + self.box_size / 2),
        )

        is_valid_move = False
        for position in self.valid_moves:
            if box_index == position:
                is_valid_move = True
        if is_valid_move:
            self.make_move(self.source, box_index)
            winner = self.check_win_both(box_index)
            if not winner:
                self.setup_next_player()
            else:
                self.drawer.draw_win(self.board, self.arena_size, winner)

        else:
            self.valid_moves.clear()
            self.drawer.redraw(self.board, self.arena_size, self.turn)
            if (
                0 <= box_index[0] < self.arena_size
                and 0 <= box_index[1] < self.arena_size
            ):
                if self.board[box_index[1]][box_index[0]] == self.turn:
                    self.mark_moves(box_index)
                self.source = box_index
                self.drawer.mark_pointer(marker_position)
            self.drawer.update()

    def make_move(self, source, target):
        self.board[target[1]][target[0]] = self.board[source[1]][source[0]]
        self.board[source[1]][source[0]] = " "

        self.drawer.redraw(self.board, self.arena_size, self.turn)
        self.valid_moves.clear()
        self.drawer.update()

    def mark_moves(self, position):
        my_pos = (
            int(position[0] * self.box_size + self.box_size / 2),
            int(position[1] * self.box_size + self.box_size / 2),
        )
        self.valid_moves.clear()
        for i in range(8):
            gutis = 1
            for moves in range(self.arena_size):
                x = position[0] + (moves + 1) * self.dx[i]
                y = position[1] + (moves + 1) * self.dy[i]
                if 0 <= x < self.arena_size and 0 <= y < self.arena_size:
                    if self.board[y][x] != " ":
                        gutis += 1
                else:
                    break
            for moves in range(self.arena_size):
                x = position[0] - (moves + 1) * self.dx[i]
                y = position[1] - (moves + 1) * self.dy[i]
                if 0 <= x < self.arena_size and 0 <= y < self.arena_size:
                    if self.board[y][x] != " ":
                        gutis += 1
                else:
                    break
            target_x = position[0] + gutis * self.dx[i]
            target_y = position[1] + gutis * self.dy[i]
            if (
                0 <= target_x < self.arena_size
                and 0 <= target_y < self.arena_size
                and self.board[target_y][target_x] != self.turn
            ):
                possible = True
                for moves in range(gutis - 1):
                    x = position[0] + (moves + 1) * self.dx[i]
                    y = position[1] + (moves + 1) * self.dy[i]
                    if (
                        self.board[y][x] != " " and self.board[y][x] != self.turn
                    ):  # opponent's guti
                        possible = False
                        break

                if possible:
                    self.valid_moves.append((target_x, target_y))
                    target_pos = (
                        int(target_x * self.box_size + self.box_size / 2),
                        int(target_y * self.box_size + self.box_size / 2),
                    )
                    pygame.draw.line(self.screen, blue, my_pos, target_pos, 2)
                    self.drawer.mark_pointer(target_pos)

    def check_win_both(self, source):
        if self.check_win(source):
            return self.board[source[1]][source[0]]

        for y in range(self.arena_size):
            for x in range(self.arena_size):
                if (
                    self.board[y][x] != " "
                    and self.board[y][x] != self.board[source[1]][source[0]]
                ):  # opponent
                    if self.check_win((x, y)):
                        return self.board[y][x]
                    else:
                        return None
        return None

    def check_win(self, source):
        visited = [[False] * self.arena_size for _ in range(self.arena_size)]
        queue = [source]
        marked = 1
        visited[source[1]][source[0]] = True

        # bfs
        while queue:
            u = queue.pop(0)
            for i in range(8):
                x = u[0] + self.dx[i]
                y = u[1] + self.dy[i]
                if (
                    0 <= x < self.arena_size
                    and 0 <= y < self.arena_size
                    and not visited[y][x]
                    and self.board[y][x] == self.board[source[1]][source[0]]
                ):
                    marked += 1
                    visited[y][x] = True
                    queue.append((x, y))

        present = 0
        for y in range(self.arena_size):
            for x in range(self.arena_size):
                if self.board[y][x] == self.board[source[1]][source[0]]:
                    present += 1

        return marked == present

    def game_intro(self):
        # close running AIs if there are any
        self.main_menu = True
        if self.machine_white:
            print("close", self.machine_white.stdin, flush=True, end="")
            self.machine_white.terminate()
            self.machine_white = None
        if self.machine_black:
            print("close", self.machine_black.stdin, flush=True, end="")
            self.machine_black.terminate()
            self.machine_black = None
        self.menu.enable()
        self.menu.mainloop(self.screen)

    def set_player_black(self, value, index):
        self.player_black = index

    def set_player_white(self, value, index):
        self.player_white = index

    def set_arena_size(self, value, index):
        if index == 0:
            self.arena_size = 8
        elif index == 1:
            self.arena_size = 6

    def board_string(self):
        board_str = "move\n"

        for y in range(self.arena_size):
            for x in range(self.arena_size):
                if self.board[y][x] == " ":
                    board_str += "."
                else:
                    board_str += self.board[y][x]
            board_str += "\n"

        return board_str

    def start_game(self):
        self.menu.disable()
        self.main_menu = False
        self.game_setup()
        self.game_loop()

    def game_loop(self):
        self.drawer.redraw(self.board, self.arena_size, self.turn)
        self.drawer.update()

        while True:
            event = pygame.event.wait()  # AIs cannot play freely if loop is stuck here

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                click_position = pygame.mouse.get_pos()
                if 400 <= click_position[0] <= 500 and 130 <= click_position[1] <= 170:
                    self.game_intro()
                if self.humans_turn:
                    self.handle_click_box(click_position)


if __name__ == "__main__":
    loa = LineOfAction()
    loa.game_intro()
