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

	def __init__(self):
		self.moves = []

	def move(self, piece, new_pos):
		start_pos = piece.position
		start_piece = deepcopy(piece)
		end_pos = new_pos
		end_piece = deepcopy(self.piece_at(*end_pos))
		white_check = self.white_in_check
		black_check = self.black_in_check
		if (piece.move(new_pos, self)):
			self.update_board()

			if (piece.color == Color.WHITE):
				self.black_in_check = self.in_check(Color.BLACK)
			else:
				self.white_in_check = self.in_check(Color.WHITE)

			self.moves.append((start_pos, start_piece, end_pos, end_piece, white_check, black_check))
			# print(self.moves)

	def move_for_check(self, piece, new_pos):
		start_pos = piece.position
		start_piece = deepcopy(piece)
		end_pos = new_pos
		end_piece = deepcopy(self.piece_at(*end_pos))
		white_check = self.white_in_check
		black_check = self.black_in_check
	
		piece.has_moved = True

		self.set_piece_at(piece.position, None)
		piece.position = new_pos
		if (piece.piece == Pieces.PAWN and ((piece.color == Color.WHITE and new_pos[1] == 7) or (piece.color == Color.BLACK and new_pos[1] == 0))):
			piece.piece = Pieces.QUEEN
		self.set_piece_at(new_pos, piece)

		self.update_board()

		if (piece.color == Color.BLACK):
			self.black_in_check = self.in_check(Color.BLACK)
		else:
			self.white_in_check = self.in_check(Color.WHITE)

		self.moves.append((start_pos, start_piece, end_pos, end_piece, white_check, black_check))
		# print(self.moves)

	def undo_last_move(self):
		if (self.moves):
			# print("Undo is being called")
			# print(f"Before: {self.moves}")
			start_pos, start_piece, end_pos, end_piece, white_check, black_check = self.moves.pop()

			self.set_piece_at(start_pos, start_piece)
			self.set_piece_at(end_pos, end_piece)


			self.update_board()

			self.black_in_check = white_check
			self.white_in_check = black_check
			# print(f"After: {self.moves}")
			return self

	def update_board(self):
		self.black_pieces = []
		self.white_pieces = []
		for row in self.board:
			for item in row:
				if (item and item.color == Color.WHITE):
					self.white_pieces.append(item)

					if (item.piece == Pieces.KING):
						self.white_king = item.position
				elif (item and item.color == Color.BLACK):
					self.black_pieces.append(item)
		
					if (item.piece == Pieces.KING):
						self.black_king = item.position
	
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

	def is_stalemated(self, color):
		white_mating_material = True
		black_mating_material = True

		num_king = 0
		num_bishop = 0
		num_knight = 0
		num_other = 0
		for item in self.white_pieces:
			if (item.piece == Pieces.KING):
				num_king += 1
			elif (item.piece == Pieces.BISHOP):
				num_bishop += 1
			elif (item.piece == Pieces.KNIGHT):
				num_knight += 1
			else:
				num_other += 1

		if (num_other == 0 and num_king == 1 and (num_bishop + num_knight) <= 1):
			white_mating_material = False

		num_king = 0
		num_bishop = 0
		num_knight = 0
		num_other = 0
		for item in self.black_pieces:
			if (item.piece == Pieces.KING):
				num_king += 1
			elif (item.piece == Pieces.BISHOP):
				num_bishop += 1
			elif (item.piece == Pieces.KNIGHT):
				num_knight += 1
			else:
				num_other += 1

		if (num_other == 0 and num_king == 1 and (num_bishop + num_knight) <= 1):
			black_mating_material = False

		if (not white_mating_material and not black_mating_material):
			return True

		if (color == Color.BLACK):
			if (self.black_in_check):
				return False

			for item in self.black_pieces:
				if (item and item.color == color):
					if len(item.generate_valid_moves(self)) > 0:
						return False
		else:
			if (self.white_in_check):
				return False

			for item in self.white_pieces:
				if (item and item.color == color):
					if len(item.generate_valid_moves(self)) > 0:
						return False
				
		return True

	def piece_at(self, x, y):
		return self.board[x][y]

	def set_piece_at(self, position, piece):
		self.board[position[0]][position[1]] = piece

	def __deepcopy__(self, memo):
		# if (self.is_copy):
		# 	return self
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
		result.moves = []

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