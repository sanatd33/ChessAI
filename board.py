from enums import *
from copy import deepcopy

class Board:
	board = [[None for x in range(8)] for y in range(8)]
	black_king = (4,7)
	white_king = (4, 0)
	black_in_check = False
	white_in_check = False
	black_pieces = []
	white_pieces = []
	is_copy = False

	def move(self, piece, new_pos):
		if (piece.move(new_pos, self)):
			self.update_board()
			if (piece.piece == Pieces.KING):
				if (piece.color == Color.WHITE):
					self.white_king = new_pos
				else:
					self.black_king = new_pos
			self.black_in_check = self.in_check(Color.BLACK)
			self.white_in_check = self.in_check(Color.WHITE)

	def update_board(self):
		self.black_pieces = []
		self.white_pieces = []
		for row in self.board:
			for item in row:
				if (item and item.color == Color.WHITE):
					self.white_pieces.append(item)
				elif (item and item.color == Color.BLACK):
					self.black_pieces.append(item)

	def in_check(self, color):
		if (color == Color.WHITE):
			for piece in self.black_pieces:
				if (piece.is_valid_move(self.white_king, self)):
					return True
			return False
		elif (color == Color.BLACK):
			for piece in self.white_pieces:
				if (piece.is_valid_move(self.black_king, self)):
					return True
			return False

	def is_checkmated(self, color):
		if (color == Color.BLACK):
			if (not self.black_in_check):
				return False
		else:
			if (not self.white_in_check):
				return False
		for row in self.board:
			for item in row:
				if (item and item.color == color):
					if len(item.generate_valid_moves(self)) > 0:
						return False
		return True

	def piece_at(self, position):
		return self.board[position[0]][position[1]]

	def piece_at(self, x, y):
		return self.board[x][y]

	def __deepcopy__(self, memo):
		if (self.is_copy):
			return self
		cls = self.__class__
		result = cls.__new__(cls)
		memo[id(self)] = result

		# Deep copy the 2D array of Piece objects
		result.board = [[deepcopy(piece, memo) if piece else None for piece in row] for row in self.board]

		# Copy other attributes
		result.black_king = deepcopy(self.black_king, memo)
		result.white_king = deepcopy(self.white_king, memo)
		result.black_in_check = deepcopy(self.black_in_check, memo)
		result.white_in_check = deepcopy(self.white_in_check, memo)
		result.black_pieces = deepcopy(self.black_pieces, memo)
		result.white_pieces = deepcopy(self.white_pieces, memo)
		result.is_copy = True

		return result

	def __str__(self):
		board = ""
		for i in reversed(range(8)):
			row = ""
			for j in range(8):
				if (self.board[j][i]):
					if (self.board[j][i].piece == Pieces.PAWN):
						row += "P"
					elif (self.board[j][i].piece == Pieces.BISHOP):
						row += "B"
					elif (self.board[j][i].piece == Pieces.KNIGHT):
						row += "N"
					elif (self.board[j][i].piece == Pieces.ROOK):
						row += "R"
					elif (self.board[j][i].piece == Pieces.QUEEN):
						row += "Q"
					elif (self.board[j][i].piece == Pieces.KING):
						row += "K"
				else:
					row += "-"
			board += row + "\n"
		return board