import chess.pgn
import torch

import numpy as np

from loader import train_model
from cnn import CNN

def fen_to_tensor_full(fen: str) -> torch.Tensor:
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

    return torch.from_numpy(tensor)

def extract_training_examples_from_pgn(file_path, max_games=1000):
    data = []

    with open(file_path, "r", encoding="utf-8") as f:
        game_count = 0

        while game_count < max_games:
            game = chess.pgn.read_game(f)
            if game is None:
                break

            result = game.headers.get("Result")
            if result not in ["1-0", "0-1", "1/2-1/2"]:
                continue

            outcome = {"1-0": 1, "0-1": -1, "1/2-1/2": 0}[result]
            board = game.board()

            for move in game.mainline_moves():
                # Store board *before* the move is made
                fen_tensor = fen_to_tensor_full(board.fen())  # shape (18, 8, 8)
                color = 1 if board.turn == chess.WHITE else -1
                data.append((fen_tensor, outcome * color))  # flip perspective
                board.push(move)

            game_count += 1

    return data

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = CNN().to(device)

    data = extract_training_examples_from_pgn("lichess_elite_2020-06.pgn", max_games=1000)
    train_model(model, data, device)
    torch.save(model.state_dict(), "chess_model.pt")
    print("Model saved to chess_model.pt")

if __name__ == "__main__":
    main()