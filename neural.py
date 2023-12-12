import numpy as np
import tensorflow as tf
from enums import *
from board import Board
from piece import Piece

class QNetwork(tf.keras.Model):
	def __init__(self, state_size, action_size):
		super(QNetwork, self).__init__()
		self.dense1 = tf.keras.layers.Dense(128, activation='relu')
		self.dense2 = tf.keras.layers.Dense(action_size, activation='linear')

	def call(self, state):
		x = self.dense1(state)
		return self.dense2(x)

class DQNAgent:
	def __init__(self, state_size, action_size, alpha=0.01, gamma=0.99, epsilon=0.1):
		self.state_size = state_size
		self.action_size = action_size
		self.alpha = alpha
		self.gamma = gamma
		self.epsilon = epsilon
		self.model = QNetwork(state_size, action_size)
		self.optimizer = tf.keras.optimizers.Adam(learning_rate=alpha)

	def choose_action(self, state, legal_moves):
		if np.random.rand() < self.epsilon:
			return legal_moves[np.random.randint(0, len(legal_moves))]
		else:
			state = np.reshape(state, (1, self.state_size))
			q_values = self.model(state)
			legal_q_values = [q_values.numpy()[0, move[0][0] * 512 + move[0][1] * 64 + move[1][0] * 8 + move[1][1]] for move in legal_moves]
			return legal_moves[np.argmax(legal_q_values)]

	def train(self, state, action, reward, next_state):
		state = np.reshape(state, (1, self.state_size))
		next_state = np.reshape(next_state, (1, self.state_size))

		with tf.GradientTape() as tape:
			q_values = self.model(state)
			target = reward + self.gamma * np.max(self.model(next_state))

			action_index = action[0][0] * 512 + action[0][1] * 64 + action[1][0] * 8 + action[1][1]
			selected_q_value = tf.gather(q_values, action_index, axis=1)

			loss = tf.keras.losses.mean_squared_error(target, selected_q_value)

		gradients = tape.gradient(loss, self.model.trainable_variables)
		self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))

def get_current_state(board):
	return encode_state(board)

def take_action(board, action, color):
	apply_move(board, action)
	return encode_state(board), calculate_reward(board, color), board.is_checkmated(get_other_value(color)) or board.is_stalemated(get_other_value(color))

def initialize_chessboard():
	board = Board()
	board.board = [[None for x in range(8)] for y in range(8)]

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

	if (color == Color.WHITE):
		return reward
	else:
		return -reward

def explore_moves(color, board):
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
	if (len(moves) == 0):
		print("ERROR NO VALID MOVES")
		print(board)
	return moves

def main():
	state_size = 8 * 8 * 3
	action_size = 8*8*8*8

	agent = DQNAgent(state_size, action_size)
	f = open("log.txt", 'w')
	num_episodes = 100
	for episode in range(num_episodes):
		f.write(f"Game: {episode}\n")
		board = initialize_chessboard()
		num_moves = 0
		total_moves = 0
		num_pieces = len(board.white_pieces) + len(board.black_pieces)
		state = get_current_state(board)
		total_reward = 0
		game_over = False
		color = Color.WHITE
		while not game_over:
			action = agent.choose_action(state, explore_moves(color, board))
			piece = board.piece_at(*action[0])
			f.write(str(action) + "\n")
			next_state, reward, game_over = take_action(board, action, color)
			agent.train(state, action, reward, next_state)
			state = next_state
			total_reward += reward
			color = get_other_value(color)
			game_over = board.is_checkmated(color)

			total_moves += 1
			if (game_over):
				f.write("Checkmate\n")
				print("Checkmate")
				print(board)
				break
			if (board.is_stalemated(color)):
				f.write("Stalemate\n")
				print("Stalemate")
				print(board)
				break

			if ((len(board.white_pieces) + len(board.black_pieces)) < num_pieces or piece.piece == Pieces.PAWN):
				num_moves = 0
				num_pieces = len(board.white_pieces) + len(board.black_pieces)
			else:
				num_moves += 1
			if (num_moves >= 200):
				f.write("Stalemate by moves\n")
				print("Stalemate by moves")
				print(board)
				break
		f.write("\n")
		print(f"Episode: {episode}, Total Reward: {total_reward}")
		del board

	f.close()
	agent.model.save_weights("chess_ai2.h5")

if __name__ == "__main__":
	main()