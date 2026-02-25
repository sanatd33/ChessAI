import chess
import torch

from concurrent.futures import ThreadPoolExecutor
from chess import Board, Move
from cnn import CNN
from utils import fen_to_tensor_full

def minimax(board: Board, depth: int, alpha: float, beta: float, model: CNN, maximizing: bool):
    if depth == 0 or board.is_game_over():
        with torch.no_grad():
            value = model(fen_to_tensor_full(board.fen()).to("cuda").unsqueeze(0)).item()
            return value if board.turn == chess.WHITE else -value

    # Move ordering: prioritize captures and checks for better pruning
    moves = sorted(board.legal_moves, key=lambda m: (
        board.is_capture(m),
        board.gives_check(m)
    ), reverse=True)

    if maximizing:
        max_eval = float('-inf')
        for move in moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, model, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, model, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def process_move(args):
    board, move, depth, model = args
    board.push(move)
    # Start with maximizing=False since we've already made our move
    eval = minimax(board, depth - 1, float('-inf'), float('inf'), model, False)
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
