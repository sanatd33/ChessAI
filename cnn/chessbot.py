import chess
import os
import torch
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

import numpy as np
import torch.nn as nn

from chess import *
from pygame import Surface
from cnn import CNN
from utils import fen_to_tensor_full
from minimax import find_best_move



WIDTH, HEIGHT = 800, 800
SQ_SIZE = WIDTH // 8
FPS = 60

PIECE_IMAGES = {}

def load_images():
    pieces = ['p', 'r', 'n', 'b', 'q', 'k']
    for color in ['w', 'b']:
        for piece in pieces:
            img_name = f"{piece}_{color}.png"
            path = os.path.join("../images", img_name)
            image = pygame.image.load(path)
            PIECE_IMAGES[color + piece] = pygame.transform.scale(image, (SQ_SIZE, SQ_SIZE))

def draw_board(screen : Surface):
    colors = [(240, 217, 181), (181, 136, 99)]
    for r in range(8):
        for c in range(8):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen : Surface, board: Board):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            piece_code = piece.symbol()
            color = 'w' if piece_code.isupper() else 'b'
            piece_type = piece_code.lower()
            screen.blit(PIECE_IMAGES[color + piece_type], pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_highlight(screen: Surface, square: int):
    """Draw a highlight around the selected square."""
    if square is not None:
        col = chess.square_file(square)
        row = 7 - chess.square_rank(square)
        highlight_color = (220, 195, 75)
        pygame.draw.rect(screen, highlight_color, pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE), 5)

def choose_best_move(board : chess.Board, model : nn.Module, device : torch.device) -> chess.Move:
    best_move = None
    best_val = float('-inf')

    for move in board.legal_moves:
        board.push(move)
        val = model(fen_to_tensor_full(board.fen()).to("cuda").unsqueeze(0))
        print(move, val)
        if val > best_val:
            best_move = move
            best_val = val
        board.pop()
    
    return best_move

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()

    load_images()
    board = chess.Board()
    model = CNN()
    model.to("cuda")
    model.load_state_dict(torch.load("chess_model_li2.pt"))

    running = True
    move_from = None

    while running:
        draw_board(screen)
        draw_pieces(screen, board)
        draw_highlight(screen, move_from)  # Highlight the selected square
        pygame.display.flip()
        clock.tick(FPS)

        if not board.is_game_over() and board.turn == chess.BLACK:
            move = find_best_move(board, 1, model)
            board.push(move)
            print("White", model(fen_to_tensor_full(board.fen()).to("cuda").unsqueeze(0)))
            # move = choose_best_move

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not board.is_game_over():
                x, y = event.pos
                col = x // SQ_SIZE
                row = 7 - (y // SQ_SIZE)
                square = chess.square(col, row)

                if move_from is None:
                    # Select the piece to move
                    if board.piece_at(square) and board.piece_at(square).color == chess.WHITE:
                        move_from = square
                else:
                    # Attempt to make the move
                    move_to = square
                    move = chess.Move(move_from, move_to)
                    if move in board.legal_moves:
                        board.push(move)
                        print("Black", model(fen_to_tensor_full(board.fen()).to("cuda").unsqueeze(0)))
                        move_from = None
                    else:
                        move_from = None  # Reset if the move is invalid
                   
        
            
    pygame.quit()

if __name__ == "__main__":
    main()
