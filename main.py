import pygame
from engine.board import Board
from ui.gui import ChessGUI

def main():
    pygame.init()
    board = Board()
    gui = ChessGUI(board)
    gui.run()
    pygame.quit()

if __name__ == "__main__":
    main()