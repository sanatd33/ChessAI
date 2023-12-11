from enum import Enum

class Color(Enum):
	WHITE = 1
	BLACK = 0

class Pieces(Enum):
	PAWN = 0
	BISHOP = 1
	KNIGHT = 2
	ROOK = 3
	QUEEN = 4
	KING = 5

def get_other_value(current_value):
	if current_value == Color.WHITE:
		return Color.BLACK
	elif current_value == Color.BLACK:
		return Color.WHITE
	else:
		raise ValueError("Invalid enum value")