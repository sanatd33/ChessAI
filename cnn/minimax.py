import chess
import torch

from concurrent.futures import ThreadPoolExecutor
from chess import Board, Move
from cnn import CNN
from utils import fen_to_tensor_full

def minimax(board: Board, depth: int, alpha: float, beta: float, model: CNN):
    if depth == 0 or board.is_game_over():
        with torch.no_grad():
            value = model(fen_to_tensor_full(board.fen()).to("cuda").unsqueeze(0)).item()
            return value if board.turn == chess.WHITE else -value  # Flip for black

    max_eval = float('-inf')
    for move in board.legal_moves:
        board.push(move)
        eval = minimax(board, depth - 1, alpha, beta, model)
        board.pop()

        max_eval = max(max_eval, eval)
        alpha = max(alpha, eval)
        if alpha >= beta:
            break

    return max_eval

def process_move(args):
    board, move, depth, model = args
    board.push(move)
    eval = minimax(board, depth - 1, float('-inf'), float('inf'), model)
    board.pop()
    return (move, eval)

def find_best_move(board: Board, depth: int, model: CNN):
    legal_moves = list(board.legal_moves)
    best_move = None
    best_eval = float('-inf')

    args_list = [(board.copy(), move, depth, model) for move in legal_moves]

    with ThreadPoolExecutor() as executor:
        for move, eval in executor.map(process_move, args_list):
            print(move, eval)
            if eval > best_eval:
                best_eval = eval
                best_move = move

    print((best_move, best_eval))
    return best_move
