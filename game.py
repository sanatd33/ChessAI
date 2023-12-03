from piece import *
from graphics import *

board = [[None for x in range(8)] for y in range(8)]

for i in range(8):
	board[i][1] = Piece((0, i), Color.WHITE, Pieces.PAWN)
	board[i][6] = Piece((0, i), Color.BLACK, Pieces.PAWN)
	if (i == 0 or i == 7):
		board[i][0] = Piece((0, i), Color.WHITE, Pieces.ROOK)
		board[i][7] = Piece((0, i), Color.BLACK, Pieces.ROOK)
	elif (i == 1 or i == 6):
		board[i][0] = Piece((0, i), Color.WHITE, Pieces.KNIGHT)
		board[i][7] = Piece((0, i), Color.BLACK, Pieces.KNIGHT)
	elif (i == 2 or i == 5):
		board[i][0] = Piece((0, i), Color.WHITE, Pieces.BISHOP)
		board[i][7] = Piece((0, i), Color.BLACK, Pieces.BISHOP)
	elif (i == 3):
		board[i][0] = Piece((0, i), Color.WHITE, Pieces.QUEEN)
		board[i][7] = Piece((0, i), Color.BLACK, Pieces.QUEEN)
	elif (i == 4):
		board[i][0] = Piece((0, i), Color.WHITE, Pieces.KING)
		board[i][7] = Piece((0, i), Color.BLACK, Pieces.KING)

win = GraphWin(width = 1000, height = 1000)
update()
key = ""
curr_piece = None
# while (key != 'Escape'):
# 	mouse = win.checkMouse()
# 	key = win.checkKey()

# 	if (mouse):
# 		x = int(mouse.getX() / 125)
# 		y = 7 - int(mouse.getY() / 125)
# 		if (not curr_piece):
# 			curr_piece = board[x][y]
# 		else:
# 			curr_piece.move((x, y), board)
# 	update()
# win.close()
win.getKey()


def update():
	for i in range(8):
		for j in range(8):
			square = Rectangle(Point(i * 125, j * 125), Point(i * 125 + 125, j * 125 + 125))
			if ((i + j) % 2 == 1):
				color = color_rgb(184, 139, 74)
			else:
				color = color_rgb(227, 193, 111)
			square.setFill(color)
			square.setOutline(color)
			square.draw(win)

			if (board[i][8-j-1]):
				x_pos = i * 125 + 60
				y_pos = j * 125 + 65
				image = Image(Point(x_pos, y_pos), "images/" + board[i][8-j-1].piece.name.lower() + "_" + board[i][8-j-1].color.name.lower() + ".png")
				image.draw(win)
	win.update()