#!/usr/bin/python3
#  agent.py
#  Nine-Board Tic-Tac-Toe Agent starter code
#  COMP3411/9814 Artificial Intelligence
#  CSE, UNSW

'''
Question: Briefly describe how your program works, including any algorithms and data structures employed, and explain any design decisions you made along the way.

Algorithm:
    My program utilises alpha-beta pruning to search through the game tree efficiently and in order to represent all moves and counter moves assuming both me and my enemy are playing optimally. To represent this algorithm, I made use of standard Python DS including arrays and dicts. Alpha beta pruning allows me to cut down significantly on the branching factor of the game tree by pruning immediately non-feasible moves from the representation of the tree, thus allowing me to look deeper into the game tree with minimal time resources.

Design Choices and Changes:
    - Initially modelled the alphabeta algorithm off the ttt.py negamax formulation, however this quickly became convoluted and bulky with the tracking of the best_move array. I decided to change the algorithm so that it only returns the evaluation amount of the move, minimising the computation carried out within the algorithm itself. Instead, as potential optimal/viable moves are uncovered with the algorithm, they are instead added to a dictionary mapping the move value to the evaluation and allowing me to either randomise or select the maximum move
    - Utility Evaluation: was initially done within the alphabeta algorithm itself, making it difficult to read and easy to misunderstand. I chose to separate move evaluation into its own function ane evaluate moves entirely based on whether they take us or the enemy closer to achieving a win

Potential Future Changes
    - I suck at tic-tac-toe and lack a lot of strategic knowledge on how to play the game and choose optimal moves. As such, my algorithm is quite "defensive", simply avoiding obviously wrong choices, but not necessarily making strategically optimal choices either. Further research into proper strategies to evaluate a move holistically combined with the alphabeta algorithm would allow my program to search deeper into the game tree and also make more high-risk high-reward moves in order to win against harder opponents

'''

import socket
import sys
import numpy as np
import typing
import copy

# a board cell can hold:
#   0 - Empty
#   1 - We played here
#   2 - Opponent played here

# the boards are of size 10 because index 0 isn't used
boards = np.zeros((10, 10), dtype="int8")
current_move = 1
s = [".","X","O"]
curr = 0 # this is the current board to play in

MAX_EVAL =  100000000 
MAX_DEPTH = 5

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
'''
Uses alphabeta minimax pruning to select the possible moves
'''
def play():
    moves = {}
    best_eval = -MAX_EVAL - MAX_DEPTH

    for cell in range(1,10):
        move = cell
        if (boards[curr][move] == 0):
            boards[curr][move] = 1
            util, win = utility_eval(curr, cell, 0)
            alpha = (-MAX_EVAL+MAX_DEPTH)-1
            beta =  MAX_EVAL+MAX_DEPTH+1
            eval = alphabeta(2, current_move, 1, cell, alpha, beta, win, util)
            boards[curr][move] = 0
            if (eval > best_eval):
                best_eval = eval
                moves.clear()
                moves.update({move: best_eval})
            elif eval == best_eval:
                moves[move] = eval
            if (best_eval > beta):
                moves[move] = eval
                break
    # print("MOVES: ", moves)
    final_move = max(moves, key=moves.get)   
    # print(f"Placing move: [{curr}]{final_move}. Had eval of: {moves[final_move]}")
    place(curr, final_move, 1)
    
    return final_move
    

#Possible combinations of cells to win a subgrid
WINNING_CELLS = [
    [1,2,3],
    [4,5,6],
    [7,8,9],
    [1,4,7],
    [2,5,8],
    [3,6,9],
    [1,5,9],
    [7,5,3]
]


'''
Get the Heuristic Evaluation of a move. Must consider:
    - If the move would be a winning move for us or the enemy
    - If the move allows the enemy to win on the next move
'''
def utility_eval(board, cell, depth):
    win = False
    eval = 0
    for triple in WINNING_CELLS:
       #If I win
        if (count_player_moves_in_triple(board, 1, triple) == 3):
            eval = MAX_EVAL - depth
            win = True
        #IF enemy wins
        elif (count_player_moves_in_triple(board, 2, triple) == 3):
           eval = -2*MAX_EVAL - depth
           win = True
        #If enemy will win on next move, low eval
        elif (count_player_moves_in_triple(board, 2, triple) == 2):
            eval -= 3000
        
        #If I have a potential triple
        elif (count_player_moves_in_triple(board, 1, triple) == 2):
            #If enemy blocks, lower eval
            if (count_player_moves_in_triple(board, 2, triple) == 1):
                eval -= 4000
            #Otherwise if i can win next round, high eval
            else:
                eval += 3000
        #If we both have a move in the triple, just chuck in a small eval
        elif (count_player_moves_in_triple(board, 1, triple) == 1 
        and count_player_moves_in_triple(board, 2, triple) == 1):
            eval += boards[board][cell]
        
    if not win:
        #When board is sparse, eval middle cells more highly
        eval += 75*boards[board][cell]

    #Return evaluation and whether the move is a winning move
    return [eval, win]

'''
Count number of moves by a player in a specific triple
'''
def count_player_moves_in_triple(board, player, triple):
    count = 0
    for i in triple:
        if boards[board][i] == player:
            count += 1
    return count

'''
Alphabeta pruning. Focuses on maximising the result for me (player 1) and minimising the result for the enemy (player 2)
Uses the evaluation function to determine which moves to make. When an ideal minimising or maximising move is found, update alpha and beta
respectively and return the evaluation
'''
def alphabeta(player, current_move, depth, board, alpha, beta, prev_move_win, acc_eval):
    if (prev_move_win or depth >= MAX_DEPTH):
        return acc_eval
    best_eval = acc_eval
    # print(f"Player {player} in board {board} at depth {depth}. BEST EVAL: {best_eval}")
    for cell in range(1,10):
        # print(f"Trying: [{board}][{cell}] for player {player}" )
        if boards[board][cell] == 0:
            boards[board][cell] = player
            # print_board(boards)
            utility, win = utility_eval(board, cell, depth)
            # print(f"Returning eval {utility} for move [{board}][{cell}] for player {player} at depth {depth}")
            this_eval = alphabeta(2-player+1, current_move, depth+1, cell, alpha, beta, win, acc_eval + utility)
            # print(f"THIS EVAL: {this_eval}. BEST EVAL: {acc_eval}")
            boards[board][cell] = 0
            if (player == 1):
                alpha = max(this_eval, alpha)
            if (player == 2):
                beta = min(this_eval, beta)
            # print(f"NEW ALPHA: {alpha} NEW BETA: {beta}")
            if (alpha >= beta):
                # print("PRUNING")
                return alpha
    if (player == 1):
        return alpha
    if player == 2:
        return beta
    

# place a move in the global boards
def place( board, num, player ):
    global curr
    curr = num
    boards[board][num] = player

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
        # print(f"First move: I placed {args[1]} in board {args[0]}.")
        place(int(args[0]), int(args[1]), 1)

        # print(f"Second move: Enemy placed {args[2]} in board {curr}.")
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
        # print(f"Last move: Enemy placed {args[0]} in board {curr}")
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
