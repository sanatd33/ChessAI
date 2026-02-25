import chess
import random
import torch
import numpy as np

import torch.nn as nn

from cnn import CNN
from loader import train_model
from multiprocessing import Queue, Process

def fen_to_tensor_full(fen: str, device : torch.device) -> torch.Tensor:
    piece_to_idx = {
        'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
        'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11,
    }

    tensor = np.zeros((18, 8, 8), dtype=np.float32)
    parts = fen.split()

    rows = parts[0].split('/')
    for r, row in enumerate(rows):
        file = 0
        for char in row:
            if char.isdigit():
                file += int(char)
            else:
                idx = piece_to_idx[char]
                tensor[idx, r, file] = 1.0
                file += 1

    if parts[1] == 'w':
        tensor[12, :, :] = 1.0
    else:
        tensor[12, :, :] = 0.0

    castling = parts[2]
    tensor[13, :, :] = 1.0 if 'K' in castling else 0.0
    tensor[14, :, :] = 1.0 if 'Q' in castling else 0.0
    tensor[15, :, :] = 1.0 if 'k' in castling else 0.0
    tensor[16, :, :] = 1.0 if 'q' in castling else 0.0

    ep_square = parts[3]
    if ep_square != '-':
        file = ord(ep_square[0]) - ord('a')
        rank = 8 - int(ep_square[1])
        tensor[17, rank, file] = 1.0

    return torch.from_numpy(tensor).to(device)

def choose_best_move(board : chess.Board, model : nn.Module, device : torch.device) -> chess.Move:
    best_move = None
    best_val = float('-inf')

    for move in board.legal_moves:
        board.push(move)
        val = model(fen_to_tensor_full(board.fen(), device).unsqueeze(0))
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
        tensor = fen_to_tensor_full(fen, device)

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