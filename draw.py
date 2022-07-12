import pygame
from colors import *


class Draw:
    def __init__(self, screen, box_size, guti_radius):
        self.screen = screen
        self.box_size = box_size
        self.guti_radius = guti_radius

    def draw_box(self, color, position):
        pygame.draw.rect(
            self.screen,
            color,
            (position[0], position[1], self.box_size, self.box_size),
            1,
        )

    def draw_guti(self, color, position):
        pygame.draw.circle(self.screen, color, position, self.guti_radius, self.guti_radius)

    def draw_board(self, board, arena_size):
        for y in range(arena_size):
            for x in range(arena_size):
                self.draw_box(black, (x * self.box_size, y * self.box_size))
                if board[y][x] == "B":
                    self.draw_guti(
                        black,
                        (
                            int(x * self.box_size + self.box_size / 2),
                            int(y * self.box_size + self.box_size / 2),
                        ),
                    )
                elif board[y][x] == "W":
                    self.draw_guti(
                        white,
                        (
                            int(x * self.box_size + self.box_size / 2),
                            int(y * self.box_size + self.box_size / 2),
                        ),
                    )

        if pygame.font:
            font = pygame.font.Font(None, 24)
            for row in range(arena_size):
                text = font.render(str(arena_size - row), 1, black)
                self.screen.blit(
                    text,
                    (
                        arena_size * self.box_size + 10,
                        row * self.box_size + self.box_size / 4,
                    ),
                )
            for col in range(arena_size):
                text = font.render(chr(ord("A") + col), 1, black)
                self.screen.blit(
                    text,
                    (
                        col * self.box_size + self.box_size / 4,
                        arena_size * self.box_size + 10,
                    ),
                )

    def write_turn(self, turn):
        next_turn = "Turn: "
        if turn == "B":
            next_turn += "BLACK"
        else:
            next_turn += "WHITE"
        if pygame.font:
            font = pygame.font.Font(None, 24)
            text = font.render(next_turn, 1, black)
            self.screen.blit(text, (400, 50))

    def mark_pointer(self, position):
        pygame.draw.circle(self.screen, green, position, 3, 3)

    def draw_back_button(self):
        pygame.draw.line(self.screen, green, (400, 150), (500, 150), 40)
        pygame.draw.rect(self.screen, black, (400, 130, 100, 40), 2)
        back_text = "<< BACK"
        if pygame.font:
            font = pygame.font.Font(None, 24)
            text = font.render(back_text, 1, black)
            self.screen.blit(text, (420, 145))

    """
     only draws the board... must update screen to make the drawings visible
    """

    def redraw(self, board, arena_size, turn):
        self.screen.fill(gold)
        self.draw_board(board, arena_size)
        self.draw_back_button()
        self.write_turn(turn)

    def draw_win(self, board, arena_size, winner):
        self.screen.fill(gold)
        self.draw_board(board, arena_size)
        self.write_win(winner)
        self.draw_back_button()
        pygame.display.update()

    def write_win(self, winner):
        win_text = ""
        if winner == "B":
            win_text += "BLACK"
        else:
            win_text += "WHITE"

        win_text += " has won"

        if pygame.font:
            font = pygame.font.Font(None, 24)
            text = font.render(win_text, 1, black)
            self.screen.blit(text, (400, 50))

    def update(self):
        pygame.display.update()
