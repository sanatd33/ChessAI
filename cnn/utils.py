import torch
import numpy as np


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

def flip_fen(fen: str, horizontal: bool = False, vertical: bool = False) -> str:

    parts = fen.strip().split()
    while len(parts) < 6:
        parts.append('0' if len(parts) == 4 else '1')
    board, turn, castling, ep, halfmove, fullmove = parts[:6]

    rows = board.split('/')

    def flip_row_h(row):
        expanded = []
        for c in row:
            if c.isdigit():
                expanded.extend(['.'] * int(c))
            else:
                expanded.append(c)
        flipped = expanded[::-1]
        out = ""
        count = 0
        for ch in flipped:
            if ch == '.':
                count += 1
            else:
                if count:
                    out += str(count)
                    count = 0
                out += ch
        if count:
            out += str(count)
        return out

    def flip_castling_h(castling):
        trans = str.maketrans("KQkq", "QKqk")
        return "".join(sorted(castling.translate(trans)))

    def flip_ep_h(ep):
        if ep == "-":
            return "-"
        file = ep[0]
        rank = ep[1]
        file_index = 7 - (ord(file) - ord('a'))
        return f"{chr(ord('a') + file_index)}{rank}"

    # Horizontal flip
    if horizontal:
        rows = [flip_row_h(row) for row in rows]
        castling = flip_castling_h(castling)
        ep = flip_ep_h(ep)

    # Vertical flip
    if vertical:
        rows = rows[::-1]
        castling = castling.swapcase()  # swap colors (K ↔ k, Q ↔ q)
        if ep != "-":
            ep_file = ep[0]
            ep_rank = str(9 - int(ep[1]))  # rank 3 ↔ 6
            ep = ep_file + ep_rank
        turn = "w" if turn == "b" else "b"

    new_board = "/".join(rows)
    return f"{new_board} {turn} {castling if castling else '-'} {ep} {halfmove} {fullmove}"
