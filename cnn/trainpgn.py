import chess.pgn
import torch

from loader import train_model
from utils import fen_to_tensor_full
from cnn import CNN

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