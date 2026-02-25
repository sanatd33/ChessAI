import chess
import random
import torch

import torch.nn as nn

from cnn import CNN
from loader import train_model
from utils import fen_to_tensor_full
from multiprocessing import Queue, Process

def choose_best_move(board : chess.Board, model : nn.Module, device : torch.device) -> chess.Move:
    best_move = chess.Move.null()
    best_val = float('-inf')

    for move in board.legal_moves:
        board.push(move)
        val = model(fen_to_tensor_full(board.fen()).to(device).unsqueeze(0))
        if val > best_val:
            best_move = move
            best_val = val
        board.pop()
    
    return best_move

def play_self_game(model : nn.Module, device) -> torch.Tensor:
    board = chess.Board()
    game_data = []

    while not board.is_game_over():
        fen = board.fen()
        tensor = fen_to_tensor_full(fen).to(device)

        if model is None or random.random() < 0.2:
            move = random.choice(list(board.legal_moves))
        else:
            move = choose_best_move(board, model, device)

        game_data.append((tensor, 1 if board.turn == chess.WHITE else -1))
        board.push(move)

    result = board.result()
    if result == '1-0':
        outcome = 1
    elif result == '0-1':
        outcome = -1
    else:
        outcome = 0

    return [(tensor, outcome * color) for tensor, color in game_data]

def self_play_worker(queue, model_state_dict, n_games):
    model = CNN()
    model.load_state_dict(model_state_dict)
    model.eval()
    model.to("cpu")  # You can also use GPU here if you have multiple

    local_data = []
    for _ in range(n_games):
        game_data = play_self_game(model, "cpu")
        local_data.extend(game_data)

    queue.put(local_data)

def run_parallel_self_play(model, total_games=100, num_workers=4):
    games_per_worker = total_games // num_workers
    queue = Queue()
    processes = []
    model_state = model.state_dict()

    for i in range(num_workers):
        p = Process(target=self_play_worker, args=(queue, model_state, games_per_worker))
        p.start()
        processes.append(p)

    all_data = []
    for _ in processes:
        all_data.extend(queue.get())

    for p in processes:
        p.join()

    return all_data

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = CNN().to(device)
    model.load_state_dict(torch.load("chess_model.pt"))

    for gen in range(10):
        print(f"\nGeneration {gen}: Self-playing games...")
        data = run_parallel_self_play(model, total_games=4, num_workers=4)
        print("Training model...")
        train_model(model, data, device)
    
if __name__ == "__main__":
    main()