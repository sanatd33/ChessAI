from board import *
from enums import *
import copy

class Piece:
	position = (0, 0)
	color = Color.WHITE
	piece = Pieces.PAWN
	has_moved = False
	is_copy = False

	def __init__(self, position, color, piece, has_moved = None):
		self.position = position
		self.color = color
		self.piece = piece
		if (has_moved):
			self.has_moved = has_moved


	def move(self, new_position, board):
		if (self.is_valid_move(new_position, board)):
			self.has_moved = True

			if (self.piece == Pieces.KING and board.piece_at(*new_position) and board.piece_at(*new_position).piece == Pieces.ROOK and board.piece_at(*new_position).color == self.color):
				if (new_position[0] == 0):
					board.set_piece_at(self.position, None)
					self.position = (2, self.position[1])
					board.piece_at(*new_position).position = (3, self.position[1])
					board.piece_at(*new_position).has_moved = True
					board.set_piece_at(self.position, self)
					board.set_piece_at(board.piece_at(*new_position).position, board.piece_at(*new_position))
					board.set_piece_at(new_position, None)
				else:
					board.set_piece_at(self.position, None)
					self.position = (6, self.position[1])
					board.piece_at(*new_position).position = (5, self.position[1])
					board.piece_at(*new_position).has_moved = True
					board.set_piece_at(self.position, self)
					board.set_piece_at(board.piece_at(*new_position).position, board.piece_at(*new_position))
					board.set_piece_at(new_position, None)
				return True

			board.set_piece_at(self.position, None)
			self.position = new_position
			if (self.piece == Pieces.PAWN and ((self.color == Color.WHITE and new_position[1] == 7) or (self.color == Color.BLACK and new_position[1] == 0))):
				self.piece = Pieces.QUEEN
			board.set_piece_at(new_position, self)
			return True

	def is_valid_target(self, new_position):
		return not (new_position[0] < 0 or new_position[0] > 7 or new_position[1] < 0 or new_position[1] > 7)

	def generate_valid_moves(self, board):
		sol = []
		if (self.piece == Pieces.PAWN):
			if (self.color == Color.WHITE):
				if (self.position != 7 and not board.piece_at(self.position[0], self.position[1] + 1)):
					new_position = (self.position[0], self.position[1] + 1)
					if (not self.results_in_check(new_position, board)):
						sol.append(new_position)
				if (self.position == 1 and not board.piece_at(self.position[0], self.position[1] + 2)):
					new_position = (self.position[0], self.position[1] + 2)
					if (not self.results_in_check(new_position, board)):
						sol.append(new_position)
				if (self.is_valid_target((self.position[0] - 1, self.position[1] + 1)) and board.piece_at(self.position[0] - 1, self.position[1] + 1) and board.piece_at(self.position[0] - 1, self.position[1] + 1).color == Color.BLACK):
					new_position = (self.position[0] - 1, self.position[1] + 1)
					if (not self.results_in_check(new_position, board)):
						sol.append(new_position)
				if (self.is_valid_target((self.position[0] + 1, self.position[1] + 1)) and board.piece_at(self.position[0] + 1, self.position[1] + 1) and board.piece_at(self.position[0] + 1, self.position[1] + 1).color == Color.BLACK):
					new_position = (self.position[0] + 1, self.position[1] + 1)
					if (not self.results_in_check(new_position, board)):
						sol.append(new_position)
			if (self.color == Color.BLACK):
				if (self.position != 0 and not board.piece_at(self.position[0], self.position[1] - 1)):
					new_position = (self.position[0], self.position[1] - 1)
					if (not self.results_in_check(new_position, board)):
						sol.append(new_position)
				if (self.position == 6 and not board.piece_at(self.position[0], self.position[1] - 2)):
					new_position = (self.position[0], self.position[1] - 2)
					if (not self.results_in_check(new_position, board)):
						sol.append(new_position)
				if (self.is_valid_target((self.position[0] - 1, self.position[1] - 1)) and board.piece_at(self.position[0] - 1, self.position[1] - 1) and board.piece_at(self.position[0] - 1, self.position[1] - 1).color == Color.WHITE):
					new_position = (self.position[0] - 1, self.position[1] - 1)
					if (not self.results_in_check(new_position, board)):
						sol.append(new_position)
				if (self.is_valid_target((self.position[0] + 1, self.position[1] - 1)) and board.piece_at(self.position[0] + 1, self.position[1] - 1) and board.piece_at(self.position[0] + 1, self.position[1] - 1).color == Color.WHITE):
					new_position = (self.position[0] + 1, self.position[1] - 1)
					if (not self.results_in_check(new_position, board)):
						sol.append(new_position)

		elif (self.piece == Pieces.BISHOP):
			directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
			for direction in directions:
				for i in range(1, 8):
					new_position = (self.position[0] + i * direction[0], self.position[1] + i * direction[1])
					if (not self.is_valid_target(new_position)):
						break
					if (not board.piece_at(*new_position)):
						if (not self.results_in_check(new_position, board)):
							sol.append(new_position)
					else:
						if (board.piece_at(*new_position).color != self.color):
							if (not self.results_in_check(new_position, board)):
								sol.append(new_position)
						break

		elif (self.piece == Pieces.KNIGHT):
			knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
			for move in knight_moves:
				new_position = (self.position[0] + move[0], self.position[1] + move[1])
				if self.is_valid_target(new_position) and (not board.piece_at(*new_position) or board.piece_at(*new_position).color != self.color):
					if (not self.results_in_check(new_position, board)):
						sol.append(new_position)

		elif self.piece == Pieces.ROOK:
			directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
			for direction in directions:
				for i in range(1, 8):
					new_position = (self.position[0] + i * direction[0], self.position[1] + i * direction[1])
					if not self.is_valid_target(new_position):
						break
					if board.piece_at(*new_position) is None:
						if (not self.results_in_check(new_position, board)):
							sol.append(new_position)
					else:
						if board.piece_at(*new_position).color != self.color:
							if (not self.results_in_check(new_position, board)):
								sol.append(new_position)
						break

		elif self.piece == Pieces.QUEEN:
			directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
			for direction in directions:
				for i in range(1, 8):
					new_position = (self.position[0] + i * direction[0], self.position[1] + i * direction[1])
					if not self.is_valid_target(new_position):
						break
					if board.piece_at(*new_position) is None:
						if (not self.results_in_check(new_position, board)):
							sol.append(new_position)
					else:
						if board.piece_at(*new_position).color != self.color:
							if (not self.results_in_check(new_position, board)):
								sol.append(new_position)
						break

		elif self.piece == Pieces.KING:
			directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
			for direction in directions:
				new_position = (self.position[0] + direction[0], self.position[1] + direction[1])
				if self.is_valid_target(new_position) and (board.piece_at(*new_position) is None or board.piece_at(*new_position).color != self.color):
					if (not self.results_in_check(new_position, board)):
						sol.append(new_position)
		return sol
	def is_valid_move(self, new_position, board):
		if (not self.is_valid_target(new_position) or self.position == new_position):
				return False
		if (self.piece == Pieces.PAWN):
			if (self.color == Color.WHITE):
				if (new_position[1] == 1 + self.position[1] and new_position[0] == self.position[0] and not board.piece_at(*new_position)):
					return True
				elif (new_position[1] == 2 + self.position[1] and new_position[0] == self.position[0] and self.position[1] == 1 and not board.piece_at(*new_position)):
					return True
				elif (new_position[1] == 1 + self.position[1] and abs(new_position[0] - self.position[0]) == 1 and board.piece_at(*new_position).color == Color.BLACK):
					return True
			if (self.color == Color.BLACK):
				if (new_position[1] == self.position[1] - 1 and new_position[0] == self.position[0] and not board.piece_at(*new_position)):
					return True
				elif (new_position[1] == self.position[1] - 2 and new_position[0] == self.position[0] and self.position[1] == 6 and not board.piece_at(*new_position)):
					return True
				elif (new_position[1] == self.position[1] - 1 and abs(new_position[0] - self.position[0]) == 1 and board.piece_at(*new_position).color == Color.WHITE):
					return True

		elif self.piece == Pieces.BISHOP:
			if abs(new_position[0] - self.position[0]) == abs(new_position[1] - self.position[1]):
				return self.check_path_clear(new_position, board)
			return False

		elif self.piece == Pieces.KNIGHT:
			delta_x = abs(new_position[0] - self.position[0])
			delta_y = abs(new_position[1] - self.position[1])
			return (delta_x == 2 and delta_y == 1) or (delta_x == 1 and delta_y == 2)

		elif self.piece == Pieces.ROOK:
			if new_position[0] == self.position[0] or new_position[1] == self.position[1]:
				return self.check_path_clear(new_position, board)
			return False

		elif self.piece == Pieces.QUEEN:
			if new_position[0] == self.position[0] or new_position[1] == self.position[1] or abs(new_position[0] - self.position[0]) == abs(new_position[1] - self.position[1]):
				return self.check_path_clear(new_position, board)
			return False

		elif self.piece == Pieces.KING:
			delta_x = abs(new_position[0] - self.position[0])
			delta_y = abs(new_position[1] - self.position[1])

			can_castle = (not self.has_moved and board.piece_at(*new_position) and board.piece_at(*new_position).piece == Pieces.ROOK and board.piece_at(*new_position).color == self.color and not board.piece_at(*new_position).has_moved)
			if (self.color == Color.WHITE):
				can_castle = can_castle and not board.white_in_check
			else:
				can_castle = can_castle and not board.black_in_check			
			can_castle = can_castle and self.check_path_castle(new_position, board)

			return (delta_x <= 1 and delta_y <= 1) or can_castle

		return False

	def check_path_clear(self, new_position, board):
		delta_x = 0 if new_position[0] == self.position[0] else (1 if new_position[0] > self.position[0] else -1)
		delta_y = 0 if new_position[1] == self.position[1] else (1 if new_position[1] > self.position[1] else -1)

		current_x, current_y = self.position[0] + delta_x, self.position[1] + delta_y
		while (current_x, current_y) != new_position:
			if board.piece_at(current_x, current_y):
				return False
			current_x += delta_x
			current_y += delta_y
		return True

	def check_path_castle(self, new_position, board):
		delta_x = 0 if new_position[0] == self.position[0] else (1 if new_position[0] > self.position[0] else -1)
		delta_y = 0 if new_position[1] == self.position[1] else (1 if new_position[1] > self.position[1] else -1)

		current_x, current_y = self.position[0] + delta_x, self.position[1] + delta_y
		while (current_x, current_y) != new_position:
			if (board.piece_at(current_x, current_y) or self.results_in_check((current_x, current_y), board)):
				return False
			current_x += delta_x
			current_y += delta_y
		return True

	def results_in_check(self, new_position, board):
		if (self.is_copy):
			board.move(self, new_position)
			if (self.color == Color.WHITE and not board.white_in_check):
				return False
			elif (self.color == Color.BLACK and not board.black_in_check):
				return False
			return True
		else:
			board_cpy = copy.deepcopy(board)
			self_cpy = copy.deepcopy(self)
			board_cpy.move(self_cpy, new_position)
			if (self.color == Color.WHITE and not board_cpy.white_in_check):
				return False
			elif (self.color == Color.BLACK and not board_cpy.black_in_check):
				return False
			return True

	def __deepcopy__(self, memo):
		if (self.is_copy):
			return self
		new_piece = self.__class__(self.position, self.color, self.piece)
		new_piece.has_moved = self.has_moved
		new_piece.is_copy = True
		return new_piece


	def __str__(self):
		return f"Piece: position={self.position}, color={self.color}, type={self.piece}"