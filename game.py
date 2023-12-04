from piece import *
from graphics import *
from board import *
from enums import *


def update_screen(win, curr_piece):
	for i in range(8):
		for j in range(8):
			square = Rectangle(Point(i * 125, j * 125), Point(i * 125 + 125, j * 125 + 125))
			if (curr_piece and curr_piece.position == (i, 7-j)):
				color = color_rgb(220, 195, 75)
			elif ((i + j) % 2 == 1):
				color = color_rgb(184, 139, 74)
			else:
				color = color_rgb(227, 193, 111)
			square.setFill(color)
			square.setOutline(color)
			square.draw(win)

			if (board.piece_at(i, 8-j-1)):
				x_pos = i * 125 + 60
				y_pos = j * 125 + 65
				image = Image(Point(x_pos, y_pos), "images/" + board.piece_at(i, 8-j-1).piece.name.lower() + "_" + board.piece_at(i, 8-j-1).color.name.lower() + ".png")
				image.draw(win)

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

win = GraphWin(width = 1000, height = 1000)
update_screen(win, None)
key = ""
curr_piece = None
curr_turn = Color.WHITE
while (key != 'Escape'):
	mouse = win.checkMouse()
	key = win.checkKey()

	if (mouse):
		x = int(mouse.getX() / 125)
		y = 7 - int(mouse.getY() / 125)
		if (not curr_piece and (not board.piece_at(x, y) or board.piece_at(x, y).color == curr_turn)):
			curr_piece = board.piece_at(x, y)
			update_screen(win, curr_piece)
		elif (curr_piece):
			if (not curr_piece.is_valid_move((x, y), board)):
				if (board.piece_at(x, y) and board.piece_at(x, y).color == curr_turn):
					curr_piece = board.piece_at(x, y)
					update_screen(win, curr_piece)
				continue
			elif (curr_piece.results_in_check((x, y), board)):
				continue
			board.move(curr_piece, (x, y))
			curr_piece = None
			if (curr_turn == Color.WHITE):
				curr_turn = Color.BLACK
			else:
				curr_turn = Color.WHITE
			if (board.is_checkmated(curr_turn)):
				print(curr_turn.name + " loses")
				update_screen(win, curr_piece)
				break
			if (board.is_stalemated(curr_turn)):
				print("Stalemate")
				update_screen(win, curr_piece)
				break
			update_screen(win, curr_piece)
while (key != 'Escape'):
	key = win.checkKey()
sys.exit()
win.close()