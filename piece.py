from enum import Enum

class Color(Enum):
	WHITE = "White"
	BLACK = "Black"

class Pieces(Enum):
	PAWN = "Pawn"
	BISHOP = "Bishop"
	KNIGHT = "Knight"
	ROOK = "Rook"
	QUEEN = "Queen"
	KING = "King"

class Piece:
	position = (0, 0)
	color = Color.WHITE
	piece = Pieces.PAWN

	def __init__(self, position, color, piece):
		self.position = position
		self.color = color
		self.piece = piece

	def move(self, new_position, board):
		if (self.is_valid(new_position, board)):
			position = new_position

	def is_valid_target(self, new_position):
		return (new_position[0] < 0 or new_position[0] > 7 or new_position[1] < 0 or new_position[1] > 7)

	def is_valid(self, new_position, board):
		if (self.piece == Pieces.PAWN):
			if (not self.is_valid_target(new_position)):
				return False
			if (self.color == Color.WHITE):
				if (new_position[1] == 1 + self.position[1] and new_position[0] == self.position[0] and not board[new_position]):
					return True
				elif (new_position[1] == 1 + self.position[1] and abs(new_position[0] - self.position[0]) == 1 and board[new_position].color == Color.BLACK):
					return True
			if (self.color == Color.BLACK):
				if (new_position[1] == self.position[1] - 1 and new_position[0] == self.position[0] and not board[new_position]):
					return True
				elif (new_position[1] == self.position[1] - 1 and abs(new_position[0] - self.position[0]) == 1 and board[new_position].color == Color.WHITE):
					return True
			return False

		return False
	def __str__(self):
		return f"Piece: position={self.position}, color={self.color}, type={self.piece}"