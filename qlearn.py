import numpy as np
from enums import *
from piece import *
from board import *


class ChessAI:
	def __init__(self, state_size, action_size):
		# Initialize Q-table with zeros
		self.Q = np.zeros((state_size, action_size))

	def choose_action(self, state):
		# Choose action with highest Q-value
		return np.argmax(self.Q[state, :])

	def train(self, state, action, reward, next_state, alpha, gamma):
		state = np.ravel(state)
		next_state = np.ravel(state)
		print(action)
		print(np.ravel(action))
		action = int(np.ravel(action)[0])
		print(action)
		print(self.Q)
		print(self.Q[state, :])
		# Q-learning update rule
		predict = self.Q[state, action]
		target = reward + gamma * np.max(self.Q[next_state, :])

		self.Q[state, action] = (1 - alpha) * predict + alpha * target

def initialize_chessboard():
	board = Board()

	for i in range(8):
		board.set_piece_at((i, 1), Piece((i, 1), Color.WHITE, Pieces.PAWN))
		board.set_piece_at((i, 6), Piece((i, 6), Color.BLACK, Pieces.PAWN))
		if (i == 0 or i == 7):
			board.set_piece_at((i, 0), Piece((i, 0), Color.WHITE, Pieces.ROOK))
			board.set_piece_at((i, 7), Piece((i, 7), Color.BLACK, Pieces.ROOK))
		elif (i == 1 or i == 6):
			board.set_piece_at((i, 0), Piece((i, 0), Color.WHITE, Pieces.KNIGHT))
			board.set_piece_at((i, 7), Piece((i, 7), Color.BLACK, Pieces.KNIGHT))
		elif (i == 2 or i == 5):
			board.set_piece_at((i, 0), Piece((i, 0), Color.WHITE, Pieces.BISHOP))
			board.set_piece_at((i, 7), Piece((i, 7), Color.BLACK, Pieces.BISHOP))
		elif (i == 3):
			board.set_piece_at((i, 0), Piece((i, 0), Color.WHITE, Pieces.QUEEN))
			board.set_piece_at((i, 7), Piece((i, 7), Color.BLACK, Pieces.QUEEN))
		elif (i == 4):
			board.set_piece_at((i, 0), Piece((i, 0), Color.WHITE, Pieces.KING))
			board.set_piece_at((i, 7), Piece((i, 7), Color.BLACK, Pieces.KING))

	board.update_board()
	return board

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

def decode_action(action_index):
	# Assuming action_index represents a pair of indices for a two-dimensional action space
	# Example: If your action space is two flattened 8x8 boards, and action_index is a number between 0 and 63 for each board
	start_row = action_index // 8
	start_column = action_index % 8
	
	# Assuming your action space has two boards, you need to calculate the index for the second board
	# You might want to adjust this part based on the specifics of your encoding
	end_board_index = start_row * 8 + start_column
	
	# Calculate the start position (row, column) and end position (row, column)
	start_position = (start_row, start_column)
	end_position = (end_board_index // 8, end_board_index % 8)
	
	return start_position, end_position



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

def explore_random_move(color, board):
	moves = []
	if (color == Color.WHITE):
		for piece in board.white_pieces:
			pieces_moves = piece.generate_valid_moves(board)
			for move in pieces_moves:
				moves.append(((piece.position[0], piece.position[1]), (move[0], move[1])))
	elif (color == Color.BLACK):
		for piece in board.black_pieces:
			pieces_moves = piece.generate_valid_moves(board)
			for move in pieces_moves:
				moves.append(((piece.position[0], piece.position[1]), (move[0], move[1])))
	if (len(moves) > 0):
		return moves[np.random.randint(0, len(moves))]
	else:
		print(board)
		return None

def apply_move(board, action):
	board.move(board.piece_at(int(action[0][0]), int(action[0][1])), (int(action[1][0]), int(action[1][1])))

def calculate_reward(board, color):
	reward = 0

	if (color == Color.WHITE):
		multiplier = 1
		reward = 0.1 * (find_num_moves(board, Color.WHITE) - find_num_moves(board, Color.BLACK))
	else:
		multiplier = -1
		reward = 0.1 * (find_num_moves(board, Color.BLACK) - find_num_moves(board, Color.WHITE))

	for white in board.white_pieces:
		if (white.piece == Pieces.KING):
			reward += 200 * multiplier
		elif (white.piece == Pieces.QUEEN):
			reward += 9 * multiplier
		elif (white.piece == Pieces.ROOK):
			reward += 5 * multiplier
		elif (white.piece == Pieces.BISHOP or white.piece == Pieces.KNIGHT):
			reward += 3 * multiplier
		elif (white.piece == Pieces.PAWN):
			reward += 1 * multiplier

	for black in board.black_pieces:
		if (black.piece == Pieces.KING):
			reward -= 200 * multiplier
		elif (black.piece == Pieces.QUEEN):
			reward -= 9 * multiplier
		elif (black.piece == Pieces.ROOK):
			reward -= 5 * multiplier
		elif (black.piece == Pieces.BISHOP or black.piece == Pieces.KNIGHT):
			reward -= 3 * multiplier
		elif (black.piece == Pieces.PAWN):
			reward -= 1 * multiplier


	return reward

# Define your state and action sizes based on your representation
state_size = 8*8*3
action_size = 4

alpha = 0.1  # Learning rate
gamma = 0.9  # Discount factor
epsilon = 0.1  # Exploration rate
num_episodes = 1000

# Create ChessAI instance
chess_ai = ChessAI(state_size, action_size)

# Training loop
for episode in range(num_episodes):
	num_moves = 0
	# Initialize the chessboard
	board = initialize_chessboard()
	curr_turn = Color.WHITE
	game_over = False

	# Play the game
	while not game_over:
		# Encode current state
		state = encode_state(board)

		# Choose action using epsilon-greedy strategy
		if np.random.rand() < epsilon:
			action = explore_random_move(curr_turn, board)
		else:
			action = decode_action(chess_ai.choose_action(state))

		# Apply the chosen move to the chessboard
		apply_move(board, action)

		# Get reward based on the move
		reward = calculate_reward(board, curr_turn)

		# Encode the new state
		next_state = encode_state(board)

		# Train the Q-learning model
		chess_ai.train(state, action, reward, next_state, alpha, gamma)

		if (curr_turn == Color.WHITE):
			curr_turn = Color.BLACK
		else:
			curr_turn = Color.WHITE
		if (board.is_checkmated(curr_turn)):
			game_over = True
		if (board.is_stalemated(curr_turn)):
			game_over = True

		num_moves += 1

	# Print progress or log information
	if episode % 100 == 0:
		print(f"Episode: {episode}, Number of Moves: {num_moves}")