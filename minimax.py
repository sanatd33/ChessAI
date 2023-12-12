from board import *
from piece import *
from enums import *
import copy
import concurrent.futures
import multiprocessing

def encode_state(board):
	flattened_board = []

	for i in range(8):
		for j in range(8):
			if (not board.piece_at(i, j)):
				flattened_board.append(-1)
				flattened_board.append(-1)
				flattened_board.append(-1)
				continue
			flattened_board.append(board.piece_at(i, j).color.value)
			flattened_board.append(board.piece_at(i, j).piece.value)
			flattened_board.append(int(board.piece_at(i, j).has_moved))

	return flattened_board

def find_num_moves(board, color):
	count = 0
	if (color == Color.WHITE):
		for piece in board.white_pieces:
			pieces_moves = piece.generate_valid_moves(board)
			count += len(pieces_moves)
	elif (color == Color.BLACK):
		for piece in board.black_pieces:
			pieces_moves = piece.generate_valid_moves(board)
			count += len(pieces_moves)
	return count

def apply_move(board, action):
	start_position, end_position = action
	board.move(board.piece_at(*start_position), end_position)

def calculate_reward(board, color):
	pawn_table = [[0,  0,  0,  0,  0,  0,  0,  0],
					[5, 10, 10,-20,-20, 10, 10,  5],
					[5, -5,-10,  0,  0,-10, -5,  5],
					[0,  0,  0, 20, 20,  0,  0,  0],
					[5,  5, 10, 25, 25, 10,  5,  5],
					[10, 10, 20, 30, 30, 20, 10, 10],
					[50, 50, 50, 50, 50, 50, 50, 50],
					[70, 70, 70, 70, 70, 70, 70, 70]]

	knight_table = [[-50,-40,-30,-30,-30,-30,-40,-50],
					[-40,-20,  0,  5,  5,  0,-20,-40],
					[-30,  5, 10, 15, 15, 10,  5,-30],
					[-30,  0, 15, 20, 20, 15,  0,-30],
					[-30,  5, 15, 20, 20, 15,  5,-30],
					[-30,  0, 10, 15, 15, 10,  0,-30],
					[-40,-20,  0,  0,  0,  0,-20,-40],
					[-50,-40,-30,-30,-30,-30,-40,-50]]

	bishop_table = [[20,-10,-10,-10,-10,-10,-10,20],
					[-10,  5,  0,  0,  0,  0,  5,-10],
					[-10, 10, 10, 10, 10, 10, 10,-10],
					[-10,  0, 10, 10, 10, 10,  0,-10],
					[-10,  5,  5, 10, 10,  5,  5,-10],
					[-10,  0,  5, 10, 10,  5,  0,-10],
					[-10,  0,  0,  0,  0,  0,  0,-10],
					[20,-10,-10,-10,-10,-10,-10,20]]

	rook_table = [[0,  0,  0,  5,  5,  0,  0,  0],
					[-5,  0,  0,  0,  0,  0,  0, -5],
					[-5,  0,  0,  0,  0,  0,  0, -5],
					[-5,  0,  0,  0,  0,  0,  0, -5],
					[-5,  0,  0,  0,  0,  0,  0, -5],
					[-5,  0,  0,  0,  0,  0,  0, -5],
					[ 5, 10, 10, 10, 10, 10, 10,  5],
					[  0,  0,  0,  0,  0,  0,  0,  0]]

	queen_table = [[-20,-10,-10, -5, -5,-10,-10,-20],
					[-10,  0,  5,  0,  0,  0,  0,-10],
					[-10,  5,  5,  5,  5,  5,  0,-10],
					[  0,  0,  5,  5,  5,  5,  0, -5],
					[ -5,  0,  5,  5,  5,  5,  0, -5],
					[-10,  0,  5,  5,  5,  5,  0,-10],
					[-10,  0,  0,  0,  0,  0,  0,-10],
					[-20,-10,-10, -5, -5,-10,-10,-20]]

	king_table = [[20, 30, 10,  0,  0, 10, 30, 20],
					[ 20, 20,  0,  0,  0,  0, 20, 20],
					[-10,-20,-20,-20,-20,-20,-20,-10],
					[-20,-30,-30,-40,-40,-30,-30,-20],
					[-30,-40,-40,-50,-50,-40,-40,-30],
					[-30,-40,-40,-50,-50,-40,-40,-30],
					[-30,-40,-40,-50,-50,-40,-40,-30],
					[-30,-40,-40,-50,-50,-40,-40,-30]]

	# reward = 0.1 * (find_num_moves(board, Color.BLACK) - find_num_moves(board, Color.WHITE))
	reward = 0

	for white in board.white_pieces:
		if (white.piece == Pieces.KING):
			reward += 200
			reward += 0.1 * king_table[white.position[0]][white.position[1]]
		elif (white.piece == Pieces.QUEEN):
			reward += 9
			reward += 0.03 * queen_table[white.position[0]][white.position[1]]
		elif (white.piece == Pieces.ROOK):
			reward += 5
			reward += 0.03 * rook_table[white.position[0]][white.position[1]]
		elif (white.piece == Pieces.BISHOP):
			reward += 3.3
			reward += 0.03 * bishop_table[white.position[0]][white.position[1]]
		elif (white.piece == Pieces.KNIGHT):
			reward += 3.2
			reward += 0.03 * knight_table[white.position[0]][white.position[1]]
		elif (white.piece == Pieces.PAWN):
			reward += 1
			reward += 0.07 * pawn_table[white.position[0]][white.position[1]]

	for black in board.black_pieces:
		if (black.piece == Pieces.KING):
			reward -= 200
			reward -= 0.1 * king_table[black.position[0]][7-black.position[1]]
		elif (black.piece == Pieces.QUEEN):
			reward -= 9
			reward -= 0.03 * queen_table[black.position[0]][7-black.position[1]]
		elif (black.piece == Pieces.ROOK):
			reward -= 5
			reward -= 0.03 * rook_table[black.position[0]][7-black.position[1]]
		elif (black.piece == Pieces.BISHOP):
			reward -= 3.3
			reward -= 0.03 * bishop_table[black.position[0]][7-black.position[1]]
		elif (black.piece == Pieces.KNIGHT):
			reward -= 3.2
			reward -= 0.03 * knight_table[black.position[0]][7-black.position[1]]
		elif (black.piece == Pieces.PAWN):
			reward -= 1
			reward -= 0.07 * pawn_table[black.position[0]][7-black.position[1]]

	if (board.white_in_check):
		reward -= 4

	if (board.black_in_check):
		reward += 4

	if (board.is_checkmated(Color.WHITE)):
		reward -= 10000000000

	if (board.is_checkmated(Color.BLACK)):
		reward += 10000000000

	# if (board.is_stalemated(Color.WHITE) or board.is_stalemated(Color.BLACK)):
	# 	reward = 0

	return reward

def explore_moves(color, board):
	moves = []
	if (color == Color.WHITE):
		for piece in board.white_pieces:
			# print(f"Before Move: {piece}")
			pieces_moves = piece.generate_valid_moves(board)
			# print(f"After Move: {piece}")
			for move in pieces_moves:
				moves.append(((piece.position[0], piece.position[1]), (move[0], move[1])))
	elif (color == Color.BLACK):
		for piece in board.black_pieces:
			# print(f"Before Move: {piece}")
			pieces_moves = piece.generate_valid_moves(board)
			# print(f"After Move: {piece}")
			for move in pieces_moves:
				moves.append(((piece.position[0], piece.position[1]), (move[0], move[1])))
	# if (len(moves) == 0):
		# print("ERROR NO VALID MOVES")
		# print(board)
	return moves

def game_over(board, color):
	return board.is_checkmated(color) or board.is_stalemated(color)

def minimax(board, depth, alpha, beta, player):
	if (depth == 0 or game_over(board, player)):
		# print(f"Eval: {calculate_reward(board, player)}")
		return calculate_reward(board, player)

	# print(f"Minimaxing, Depth: {depth}, Color: {player}")
	# print(board)

	legal_moves = explore_moves(player, board)
	# print(f"Legal Moves: {legal_moves}\n")

	# print("After finding all legal moves")
	# print(board)

	if (player == Color.WHITE):
		max_eval = float('-inf')
		for move in legal_moves:
			# print(f"Move: {move}, Depth: {depth}")

			# board_cpy = copy.deepcopy(board)

			# print("Before Move")
			# print(board)
			apply_move(board, move)
			# print("After Move")
			# print(board)

			eval = minimax(board, depth - 1, alpha, beta, get_other_value(player))
			# print("I am calling undo in minimax line 207")
			board = board.undo_last_move()
			# if (undo):
				# board = undo
			# print("Undo Move")
			# print(board)


			max_eval = max(max_eval, eval)
			alpha = max(alpha, eval)

			if (beta <= alpha):
				break
		return max_eval
	else:
		min_eval = float('inf')
		for move in legal_moves:
			# print(f"Move: {move}, Depth: {depth}")

			# board_cpy = copy.deepcopy(board)
			# print("Before Move")
			# print(board)
			apply_move(board, move)
			# print("After Move")
			# print(board)


			eval = minimax(board, depth - 1, alpha, beta, get_other_value(player))
			# print("I am calling undo in minimax line 230")
			board = board.undo_last_move()
			# if (undo):
				# board = undo
			# print("Undo Move")
			# print(board)

			min_eval = min(min_eval, eval)
			beta = min(beta, eval)

			if (beta <= alpha):
				break
		return min_eval

def find_best_move(board, depth, color):
	# print("Finding Best Moves")
	# print(board)
	legal_moves = explore_moves(color, board)
	# print(f"Legal Moves: {legal_moves}")
	best_move = None

	if (color == Color.WHITE):
		best_eval = float('-inf')
	else:
		best_eval = float('inf')
	alpha = float('-inf')
	beta = float('inf')

	for move in legal_moves:
		# print(f"Move: {move}, Depth: {depth}")
		# board_cpy = copy.deepcopy(board)

		apply_move(board, move)
		eval = minimax(board, depth - 1, alpha, beta, get_other_value(color))
		# print("I am calling undo in minimax line 262")
		undo = board.undo_last_move()
		if (undo):
			board = undo

		# print(f"Move: {move}, Depth: {depth}, Eval: {eval}")

		if (color == Color.WHITE and eval > best_eval):
			best_eval = eval
			best_move = move
			alpha = max(alpha, eval)
		elif (color == Color.BLACK and eval < best_eval):
			best_eval = eval
			best_move = move
			beta = min(beta, eval)

	# print(f"Best Move: {best_move}")
	# print(f"Best Eval: {best_eval}")
	return best_move

def minimax_parallel(board, depth, alpha, beta, player, executor):
	if depth == 0 or game_over(board, player):
		# print(f"Eval: {calculate_reward(board, player)}")
		return calculate_reward(board, player)

	# print(f"Minimaxing, Depth: {depth}, Color: {player}")
	# print(board)

	legal_moves = explore_moves(player, board)
	# print(f"Legal Moves: {legal_moves}\n")

	if player == Color.WHITE:
		max_eval = float('-inf')
		futures = []
		for move in legal_moves:
			# print(f"Move: {move}, Depth: {depth}")

			apply_move(board, move)
			futures.append(executor.submit(minimax_parallel, board, depth - 1, alpha, beta, get_other_value(player), executor))

		for future in concurrent.futures.as_completed(futures):
			board = board.undo_last_move()
			eval = future.result()
			max_eval = max(max_eval, eval)
			alpha = max(alpha, eval)

			if beta <= alpha:
				break

		return max_eval
	else:
		min_eval = float('inf')
		futures = []
		for move in legal_moves:
			# print(f"Move: {move}, Depth: {depth}")
			apply_move(board, move)
			futures.append(executor.submit(minimax_parallel, board, depth - 1, alpha, beta, get_other_value(player), executor))

		for future in concurrent.futures.as_completed(futures):
			board = board.undo_last_move()
			eval = future.result()
			min_eval = min(min_eval, eval)
			beta = min(beta, eval)

			if beta <= alpha:
				break

		return min_eval

def process_move_base(board, move, depth, alpha, beta, moves, color):
	best_move = None
	if color == Color.WHITE:
		best_eval = float('-inf')
	else:
		best_eval = float('inf')

	apply_move(board, move)
	eval = minimax(board, depth - 1, alpha, beta, get_other_value(color))
	undo = board.undo_last_move()
	if (undo):
		board = undo

	if (color == Color.WHITE and eval > best_eval):
		best_eval = eval
		best_move = move
		alpha = max(alpha, eval)
	elif (color == Color.BLACK and eval < best_eval):
		best_eval = eval
		best_move = move
		beta = min(beta, eval)

	moves.append((best_move, best_eval))

def find_best_move_parallel(board, depth, color):
	# print("Finding Best Moves")
	# print(board)
	legal_moves = explore_moves(color, board)

	best_move = None
	alpha = float('-inf')
	beta = float('inf')
	
	# print(f"Legal Moves: {legal_moves}")

	if color == Color.WHITE:
		best_eval = float('-inf')
	else:
		best_eval = float('inf')

	futures = []
	moves = multiprocessing.Manager().list()
	for move in legal_moves:
		# print(f"Move: {move}, Depth: {depth}")
		
		process = multiprocessing.Process(target=process_move_base, args=(board, move, depth - 1, alpha, beta, moves, color))
		process.start()
		futures.append(process)

	for process in futures:
		process.join()

	for action in moves:
		move, eval = action
		if (color == Color.WHITE and eval > best_eval):
			best_eval = eval
			best_move = move
		elif (color == Color.BLACK and eval < best_eval):
			best_eval = eval
			best_move = move

	# for move, future in zip(legal_moves, concurrent.futures.as_completed(futures)):
	# 	board = board.undo_last_move()
	# 	eval = future.result()

	# 	if color == Color.WHITE and eval > best_eval:
	# 		best_eval = eval
	# 		best_move = move
	# 		alpha = max(alpha, eval)
	# 	elif color == Color.BLACK and eval < best_eval:
	# 		best_eval = eval
	# 		best_move = move
	# 		beta = min(beta, eval)

	# print(f"Best Move: {best_move}")
	# print(f"Best Eval: {best_eval}")

	return best_move