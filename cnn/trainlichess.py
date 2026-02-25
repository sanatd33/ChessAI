import torch
import json
import random
import numpy as np

from loader import train_model
from utils import flip_fen
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

def extract_from_lichess_eval_json(filepath, max_positions=50000):
    import json
    import random

    data = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f):
            if line_num >= max_positions:
                break

            try:
                entry = json.loads(line)
                fen = entry["fen"]

                if fen.count(" ") < 5:
                    fen += " 0 1"

                evals = entry.get("evals", [])
                if not evals or not evals[0]["pvs"]:
                    continue

                pv = evals[0]["pvs"][0]

                if "cp" in pv:
                    value = max(min(pv["cp"], 10000), -10000)
                elif "mate" in pv:
                    mate_score = 10000 - abs(pv["mate"]) * 100
                    value = mate_score if pv["mate"] > 0 else -mate_score
                else:
                    continue

                turn = fen.split()[1]
                if turn == 'b':
                    value = -value

                tensor = fen_to_tensor_full(fen)
                data.append((tensor, value))

                h_fen = flip_fen(fen, horizontal=True)
                data.append((fen_to_tensor_full(h_fen), value))

                v_fen = flip_fen(fen, vertical=True)
                data.append((fen_to_tensor_full(v_fen), -value))

                hv_fen = flip_fen(fen, horizontal=True, vertical=True)
                data.append((fen_to_tensor_full(hv_fen), -value))

            except (json.JSONDecodeError, KeyError, ValueError):
                continue

    print(f"✅ Extracted and augmented {len(data)} training positions.")
    return data


def balance_eval_data(data, loss_thresh=-2500, win_thresh=2500):
    losses = [x for x in data if x[1] < loss_thresh]
    draws  = [x for x in data if loss_thresh <= x[1] <= win_thresh]
    wins   = [x for x in data if x[1] > win_thresh]

    min_len = min(len(losses), len(draws), len(wins))

    # balanced = losses[:min_len] + draws[:min_len] + wins[:min_len]
    balanced = draws
    print(f"Balancing dataset: using {len(balanced)} positions.")
    random.shuffle(balanced)
    return balanced


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = CNN().to(device)
    model.load_state_dict(torch.load("chess_model_li2.pt"))

    data = extract_from_lichess_eval_json("lichess_db_eval.jsonl", max_positions=50000)
    data = balance_eval_data(data)
    train_model(model, data, device)
    torch.save(model.state_dict(),   "chess_model_li2.pt")
    print("Model saved to chess_model_li.pt")

if __name__ == "__main__":
    main()