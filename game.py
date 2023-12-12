from piece import *
from graphics import *
from board import *
from enums import *
# from neural import DQNAgent, get_current_state, explore_moves, take_action
from minimax import find_best_move, apply_move, find_best_move_parallel
import cProfile
import yappi


def update_screen(win, board, curr_piece):
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

def main():
	board = initialize_chessboard()

	# state_size = 8 * 8 * 3  # Assuming your encode_state function returns a flattened representation
	# action_size = 8*8*8*8  # Assuming your action space is represented by a pair of indices

	# agent = DQNAgent(state_size, action_size)
	# agent.model.build((action_size, state_size))
	# agent.model.load_weights("chess_ai2.h5")

	win = GraphWin(width = 1000, height = 1000)
	update_screen(win, board, None)
	key = ""
	curr_piece = None
	curr_turn = Color.WHITE

	i = 0

	profiler = cProfile.Profile()
	while (key != 'Escape'):
		if (curr_turn == Color.BLACK):
			# state = get_current_state(board)
			# action = agent.choose_action(state, explore_moves(curr_turn, board))
			# next_state, reward, game_over = take_action(board, action, curr_turn)

			profiler.enable()
			move = find_best_move_parallel(board, 5, curr_turn)
			profiler.disable()
			profiler.dump_stats(f'profiles/profile_data_{i+1}.prof')
			apply_move(board, move)

			if (curr_turn == Color.WHITE):
				curr_turn = Color.BLACK
			else:
				curr_turn = Color.WHITE
			if (board.is_checkmated(curr_turn)):
				print(curr_turn.name + " loses")
				update_screen(win, board, curr_piece)
				break
			if (board.is_stalemated(curr_turn)):
				print("Stalemate")
				update_screen(win, board, curr_piece)
				break
			update_screen(win, board, curr_piece)
			i += 1
			continue


		mouse = win.checkMouse()
		key = win.checkKey()

		if (mouse):
			x = int(mouse.getX() / 125)
			y = 7 - int(mouse.getY() / 125)
			if (not curr_piece and (not board.piece_at(x, y) or board.piece_at(x, y).color == curr_turn)):
				curr_piece = board.piece_at(x, y)
				update_screen(win, board, curr_piece)
			elif (curr_piece):
				if (not curr_piece.is_valid_move((x, y), board)):
					if (board.piece_at(x, y) and board.piece_at(x, y).color == curr_turn):
						curr_piece = board.piece_at(x, y)
						update_screen(win, board, curr_piece)
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
					update_screen(win, board, curr_piece)
					break
				if (board.is_stalemated(curr_turn)):
					print("Stalemate")
					update_screen(win, board, curr_piece)
					break
				update_screen(win, board, curr_piece)
	while (key != 'Escape'):
		key = win.checkKey()
	sys.exit()
	win.close()

if (__name__ == "__main__"):
	# board = initialize_chessboard()

	# yappi.set_clock_type("wall")
	# yappi.start()
	# find_best_move(board, 5, Color.WHITE)

	# yappi.stop()
	# yappi.get_func_stats().print_all()
	# yappi.get_thread_stats().print_all()
	main()