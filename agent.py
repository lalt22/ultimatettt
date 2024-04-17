#!/usr/bin/python3
#  agent.py
#  Nine-Board Tic-Tac-Toe Agent starter code
#  COMP3411/9814 Artificial Intelligence
#  CSE, UNSW

import socket
import sys
import numpy as np
import typing

# a board cell can hold:
#   0 - Empty
#   1 - We played here
#   2 - Opponent played here

# the boards are of size 10 because index 0 isn't used
boards = np.zeros((10, 10), dtype="int8")
# move = np.zeros((10,10), dtype="int8")
best_move = np.ones(81, dtype="int8")
current_move = 1
s = [".","X","O"]
curr = 0 # this is the current board to play in

MIN_EVAL = -1000000 #alpha
MAX_EVAL =  1000000 #beta

# print a row
def print_board_row(bd, a, b, c, i, j, k):
    print(" "+s[bd[a][i]]+" "+s[bd[a][j]]+" "+s[bd[a][k]]+" | " \
             +s[bd[b][i]]+" "+s[bd[b][j]]+" "+s[bd[b][k]]+" | " \
             +s[bd[c][i]]+" "+s[bd[c][j]]+" "+s[bd[c][k]])

# Print the entire board
def print_board(board):
    print_board_row(board, 1,2,3,1,2,3)
    print_board_row(board, 1,2,3,4,5,6)
    print_board_row(board, 1,2,3,7,8,9)
    print(" ------+-------+------")
    print_board_row(board, 4,5,6,1,2,3)
    print_board_row(board, 4,5,6,4,5,6)
    print_board_row(board, 4,5,6,7,8,9)
    print(" ------+-------+------")
    print_board_row(board, 7,8,9,1,2,3)
    print_board_row(board, 7,8,9,4,5,6)
    print_board_row(board, 7,8,9,7,8,9)
    print()

# choose a move to play
def play():
    # print_board(boards)
    print(f"Playing move in board: {curr}. Current move is {current_move}")
    # just play a random move for now
    # n = np.random.randint(1,9)
    # while boards[curr][n] != 0:
        # n = np.random.randint(1,9)
    alphabeta(1, current_move, 1, curr, MIN_EVAL, MAX_EVAL, best_move)
    return_val = best_move[current_move]
    print(f"playing {return_val} in grid {curr}", )
    print("Returning: ",  return_val)
    place(curr, return_val, 1)
    
    return return_val

def alphabeta( player, current_move, cell, board, alpha, beta, best_move ):
    print(f"Testing player {player}, move [{board}][{best_move[cell]}], sub-grid {board}, alpha {alpha}, beta {beta}")
    print_board(boards)
    best_eval = MIN_EVAL

    # If enemy wins, return a very low eval
    if game_won(2-player+1):
        print(f"Player {2-player+1} wins with this move: [{board}][{best_move[cell]}]")
        return -1000 + cell

    this_move = 0
    for r in range(1,10):
        print(f"Trying square {r} in board {board}: {boards[board][r]}")
        if boards[board][r] == 0:
            print("Testing empty cell: ", boards[board][r])
            this_move = r
            boards[board][this_move] = player
            print(f"Set cell [{board}][{this_move}] to {boards[board][this_move]}\n")
            if (cell < 9):
                this_eval = -alphabeta((2-player+1), current_move, cell+1, r, -beta, -alpha, best_move)
                print(f'Best Eval: {best_eval} This Eval: {this_eval}')
                boards[board][this_move] = 0
                print(f"Unset cell [{board}][{this_move}] to {boards[board][this_move]}")
                if this_eval > best_eval:
                    best_move[current_move] = this_move
                    best_eval = this_eval
                    if best_eval > alpha:
                        alpha = best_eval
                        if alpha >= beta:
                            print("Cutoff\n")
                            return (alpha)
    if this_move == 0:
        print(f"No legal moves for {player}\n")
        return (0)
    else:
        print(f"Alpha return for move [{board}][{best_move[cell]}] by player {player}")
        return (alpha)
    pass

# place a move in the global boards
def place( board, num, player ):
    global curr
    curr = num
    boards[board][num] = player

def board_won(p: int, bd: int):
    return(  ( boards[bd][1] == p and boards[bd][2] == p and boards[bd][3] == p)
           or( boards[bd][4] == p and boards[bd][5] == p and boards[bd][6] == p )
           or( boards[bd][7] == p and boards[bd][8] == p and boards[bd][9] == p )
           or( boards[bd][1] == p and boards[bd][4] == p and boards[bd][7] == p )
           or( boards[bd][2] == p and boards[bd][5] == p and boards[bd][8] == p )
           or( boards[bd][3] == p and boards[bd][6] == p and boards[bd][9] == p )
           or( boards[bd][1] == p and boards[bd][5] == p and boards[bd][9] == p )
           or( boards[bd][3] == p and boards[bd][5] == p and boards[bd][7] == p ))


def game_won( p: int ):
    print(f"Checking if player {p} wins with this move")
    for i in range(1,10):
        if (board_won(p, i)):
            return True
    return False



# read what the server sent us and
# parse only the strings that are necessary
def parse(string):
    global current_move
    if "(" in string:
        command, args = string.split("(")
        args = args.split(")")[0]
        args = args.split(",")
    else:
        command, args = string, []

    # init tells us that a new game is about to begin.
    # start(x) or start(o) tell us whether we will be playing first (x)
    # or second (o); we might be able to ignore start if we internally
    # use 'X' for *our* moves and 'O' for *opponent* moves.

    # second_move(K,L) means that the (randomly generated)
    # first move was into square L of sub-board K,
    # and we are expected to return the second move.
    if command == "second_move":
        # place the first move (randomly generated for opponent)
        place(int(args[0]), int(args[1]), 2)
        print(f"First move: Enemy placed {args[1]} in board {args[0]}.")
        current_move = 2
        return play()  # choose and return the second move

    # third_move(K,L,M) means that the first and second move were
    # in square L of sub-board K, and square M of sub-board L,
    # and we are expected to return the third move.
    elif command == "third_move":
        # place the first move (randomly generated for us)
        #potential TODO: dont randomly generate first move - choose methodically
        print(f"First move: I placed {args[1]} in board {args[0]}.")
        place(int(args[0]), int(args[1]), 1)

        print(f"Second move: Enemy placed {args[2]} in board {curr}.")
        # place the second move (chosen by opponent)
        place(curr, int(args[2]), 2)
        
        # global current_move
        current_move = 3
        return play() # choose and return the third move

    # nex_move(M) means that the previous move was into
    # square M of the designated sub-board,
    # and we are expected to return the next move.
    elif command == "next_move":
        # place the previous move (chosen by opponent)
        print(f"Last move: Enemy placed {args[0]} in board {curr}")
        place(curr, int(args[0]), 2)
        
        # global current_move
        current_move = current_move + 2
        return play() # choose and return our next move

    elif command == "win":
        print("Yay!! We win!! :)")
        return -1

    elif command == "loss":
        print("We lost :(")
        return -1

    return 0

# connect to socket
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(sys.argv[2]) # Usage: ./agent.py -p (port)

    s.connect(('localhost', port))
    while True:
        text = s.recv(1024).decode()
        if not text:
            continue
        for line in text.split("\n"):
            response = parse(line)
            if response == -1:
                s.close()
                return
            elif response > 0:
                s.sendall((str(response) + "\n").encode())

if __name__ == "__main__":
    main()
