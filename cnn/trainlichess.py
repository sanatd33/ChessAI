import torch
import json
import random

from loader import train_model
from utils import flip_fen, fen_to_tensor_full
from cnn import CNN

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
    if min_len == 0:
        # Fall back to using all data if one category is empty
        balanced = data
    else:
        balanced = losses[:min_len] + draws[:min_len] + wins[:min_len]
    print(f"Balancing dataset: {len(losses)} losses, {len(draws)} draws, {len(wins)} wins -> {len(balanced)} positions.")
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