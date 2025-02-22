# The Royal Game of Ur

import random
import sys
from operator import itemgetter, attrgetter, methodcaller


def show_notes():
    print('The Royal Game of Ur was translated to code by Ryan W. Kasten')
    print("(rwkasten at most Internet places you can think of - if in doubt, that's my gmail address)")
    print()
    print("It was adapted from the Masters ruleset at https://www.mastersofgames.com/rules/royal-ur-rules.htm")
    print("Or https://archive.is/UYPWG for an archived version.")
    print("You may find some of the game's fascinating history on that page. You may also note that no one seems")
    print("to know exactly how to play the game. Of the rulesets listed on that page, I liked the Masters one")
    print("the best, so that's what I went with.")
    print()
    print("The game is currently in alpha. Here are my notes for things to add/fix:")
    print("Bugs - none known")
    print("To-dos(minor): messages for invalid bear-off attempt, blocked move")
    print("To-dos: expand the path list to include an explicit index to allow markers to hit the same square twice")
    print("To-dos: AI: selectColor, getComputerMove, getDupeBoard, canHit, canBearOff, hitRosette, escapeOpponent")
    print("To-dos: V2: secondary rulesets + instructions, pot multipliers")
    print("To-dos: V3: wagering, W/L tracking, graphics + touch/click I/O")
    print("Possible to-dos: add option for path arrows")
    print()
    print("Thanks for reading!")
    print()


def draw_board(board):
    """Prints an Ur game board"""
    HLINE1 = ' +---+---+---+---+       +---+---+'
    HLINE2 = ' +---+---+---+---+---+---+---+---+'

    print('   1   2   3   4   5   6   7   8')
    print(HLINE1)
    for y in range(3):
        print(str(y + 1) + '|', end='')
        for x in range(8):
            if (x == 4 and y == 0) or (x == 4 and y == 2):
                print('    ', end='')
            elif (x == 5 and y == 0) or (x == 5 and y == 2):
                print('   |', end='')
            elif is_rosette(x, y):
                print('R%s |' % (board[x][y]), end='')
            else:
                print(' %s |' % (board[x][y]), end='')
        if y == 0 or y == 1:
            print('\n' + HLINE2)
        else:
            print('\n' + HLINE1)


def draw_ingame_board(board, w_off, b_off):
    """Prints an Ur game board with reserve and off counts"""
    w_reserve = pieces_reserve(board, 'W', w_off)
    b_reserve = pieces_reserve(board, 'B', b_off)
    HLINE2 = ' +---+---+---+---+---+---+---+---+'

    print('   1   2   3   4   5   6   7   8')
    print(' +---+---+---+---+   W   +---+---+')
    for y in range(3):
        print(str(y + 1) + '|', end='')
        for x in range(8):
            if x == 4 and y == 0:
                print('%s  ' % w_reserve, end='')
            elif x == 4 and y == 2:
                print('%s  ' % b_reserve, end='')
            elif x == 5 and y == 0:
                print('   %s|' % w_off, end='')
            elif x == 5 and y == 2:
                print('   %s|' % b_off, end='')
            elif is_rosette(x, y):
                print('R%s |' % (board[x][y]), end='')
            else:
                print(' %s |' % (board[x][y]), end='')
        if y == 0 or y == 1:
            print('\n' + HLINE2)
        else:
            print('\n' + ' +---+---+---+---+   B   +---+---+')


def reset_board():
    """Sets all spaces on an Ur board to blank"""
    board = []
    for x in range(8):
        board.append([' '] * 3)
    return board


def is_rosette(x, y):
    """Decide whether a square has a rosette on it or not"""
    if (x == 0 and y == 0) or (x == 6 and y == 0) or (x == 3 and y == 1) or (x == 0 and y == 2) or (x == 6 and y == 2):
        return True
    else:
        return False


def black_path():
    """This will be selectable as additional rulesets are added"""
    b_path = [[3, 2], [2, 2], [1, 2], [0, 2], [0, 1], [1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [6, 0], [7, 0],
              [7, 1], [7, 2], [6, 2]]
    return b_path


def white_path():
    """This will be selectable as additional rulesets are added"""
    w_path = [[3, 0], [2, 0], [1, 0], [0, 0], [0, 1], [1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [6, 2], [7, 2],
              [7, 1], [7, 0], [6, 0]]
    return w_path


def dice_roll():
    """Returns a random number between 0 and 3. Can be extended for different numbers of dice"""
    rollem = random.randint(0, 3)
    if rollem == 0:
        return 4
    else:
        return rollem


def pieces_reserve(board, marker, pieces_off):
    """Checks for number of player's pieces yet to enter the board"""
    reserve = 7
    for x in range(8):
        for y in range(3):
            if board[x][y] == marker:
                reserve -= 1
    return reserve - pieces_off


def get_on_board_pieces(board, player):
    """Get list of player's markers currently on the board"""
    on_board_pieces = []
    for x in range(8):
        for y in range(3):
            if board[x][y] == player:
                on_board_pieces.append([x, y])
    return on_board_pieces


def is_valid_selection(board, player, movex, movey):
    """Has the player selected one of their own pieces to move?"""
    if board[movex][movey] == player:
        return True
    else:
        return False


def is_bearing_off(path, roll, movex, movey):
    """Does this move bear a piece off?"""
    if movex == 'o' and movey == 'n':
        return False
    where_path = path.index([movex, movey])
    if where_path + roll == len(path):
        return True
    else:
        return False


def is_move_valid(board, player, path, roll, movex, movey):
    """Is the proposed move a valid one?"""
    if not is_valid_selection(board, player, movex, movey):
        return False
    if is_bearing_off(path, roll, movex, movey):
        return True
    where_path = path.index([movex, movey])
    if where_path + roll > len(path):
        return False
    pathx, pathy = path[where_path + roll]
    if board[pathx][pathy] != player:
        return True
    else:
        return False


def is_bear_on_valid(board, player, path, roll):
    """Is bearing on allowed with this roll?"""
    pathx, pathy = path[roll-1]
    if board[pathx][pathy] == player:
        return False
    else:
        return True


def make_move(board, player, path, roll, movex, movey):
    """Take the piece at location and move it down the path"""
    where_path = path.index([movex, movey])
    board[movex][movey] = ' '
    if not is_bearing_off(path, roll, movex, movey):
        pathx, pathy = path[where_path + roll]
        board[pathx][pathy] = player
    return board


def is_bearing_on(board, player, path, roll):
    """Bear a player's piece onto the board. Assumes validity has already been checked."""
    pathx, pathy = path[roll - 1]
    board[pathx][pathy] = player


def who_goes_first():
    # Randomly choose the player who goes first.
    if random.randint(0, 1) == 0:
        return 'B'
    else:
        return 'W'


def get_player_move(board, player, path, roll, off):
    # Let the player type in their move.
    # Returns the move as [x, y] (or returns the strings 'hints' or 'quit')
    DIGITS1TO8 = '1 2 3 4 5 6 7 8'.split()
    DIGITS1TO3 = '1 2 3'.split()
    while True:
        if player == 'B':
            playername = 'black'
        else:
            playername = 'white'
        print(playername.capitalize() + " rolled a " + str(roll) + ". Please select a piece to move.", end=' ')
        if pieces_reserve(board, player, off) > 0:
            print("To bear on, type 'on'.", end=' ')
        print("To quit, type 'quit'.")

        move = input().lower()
        if move == 'on':
            if pieces_reserve(board, player, off) == 0:
                print("No reserve pieces!", end=' ')
                continue
            elif is_bear_on_valid(board, player, path, roll):
                return 'on'
            else:
                print("Can't bear on with that roll!")
        if move.lower().startswith('q'):
            return 'quit'

        if len(move) == 2 and move[0] in DIGITS1TO8 and move[1] in DIGITS1TO3:
            x = int(move[0]) - 1
            y = int(move[1]) - 1
            if not is_move_valid(board, player, path, roll, x, y):
                continue
            else:
                break
        else:
            print('That is not a valid move. Type the x digit (1-8), then the y digit (1-8).')
            print('For example, 81 will be the top-right corner.')

    return [x, y]


def get_landing_square(path, roll, movex, movey):
    """Figure out where a particular roll will put a marker that starts at movex, movey"""
    if movex == 'o' and movey == 'n':
        return path[roll-1]
    else:
        where_path = path.index([movex, movey])
        if is_bearing_off(path, roll, movex, movey):
            return '[4,2]'
        else:
            pathx, pathy = path[where_path + roll]
            return [pathx, pathy]


def can_bear_on(board, player, path, off, roll):
    """See if the player can bear on"""
    if pieces_reserve(board, player, off) < 1:
        return False
    if is_bear_on_valid(board, player, path, roll):
        return True
    else:
        return False


def valid_moves(board, pieces_off, player, path, roll):
    """Check for valid player moves and return the list"""
    moves = []
    on_board_pieces = get_on_board_pieces(board, player)

    # Can player bear off?
    pathx, pathy = path[len(path) - roll]
    if board[pathx][pathy] == player:
        moves.append([pathx, pathy])

    # Go down the list of on-board pieces and see if any of them can legally move
    for piece in range(len(on_board_pieces)):
        piecex, piecey = on_board_pieces[piece]
        where_path = path.index([piecex, piecey])
        if where_path + roll < len(path):  # equality already considered and exceeds fails by default
            pathx, pathy = path[where_path + roll]
            if board[pathx][pathy] != player:
                moves.append(on_board_pieces[piece])

    # Can player bear on?
    if len(on_board_pieces) == 0 and pieces_off < 7:
        # Pieces in reserve + none on the board = can bear on
        moves.append(['o', 'n'])
    elif pieces_reserve(board, player, pieces_off) > 0:
        pathx, pathy = path[roll - 1]
        if board[pathx][pathy] != player:
            moves.append(['o', 'n'])

    return moves


def get_computer_move(board, player, path, roll, w_off, b_off):
    """This function selects a move for a computer player"""
    weight: int = 0
    move_weights = []
    home_board = path[:4]
    if player == 'W':
        off = w_off
        opponent = 'B'
        opponent_path = black_path()
        opponent_off = b_off
    else:
        off = b_off
        opponent = 'W'
        opponent_path = white_path()
        opponent_off = w_off
    possible_moves = valid_moves(board, off, player, path, roll)
    opponent_pieces = get_on_board_pieces(board, opponent)
    for move in possible_moves:
        # Can bear off - if this is found, immediately return the value
        pathx, pathy = path[len(path) - roll]
        if board[pathx][pathy] == player:
            return move
        # Can hit - high priority
        weight = 0
        landx, landy = get_landing_square(path, roll, move[0], move[1])
        if board[landx][landy] == opponent:
            weight += 10
        # Is it a rosette?
        if is_rosette(landx, landy):
            weight += 7
        # Will piece stay in home board?
        if [landx, landy] in home_board:
            weight += 3
        # Will it get out of range of opponent?
        # land_square = [landx, landy]
        # print(land_square)
        # if land_square in opponent_path:
        #     for square in opponent_pieces:
        #         squares_away = 0
        #         where_path = opponent_path.index([landx, landy])
        #         opponent_path = path.index(square)
        #         if where_path - opponent_path > squares_away:
        #             squares_away = where_path - opponent_path
        #     if squares_away > 4:
        #         weight += 2
        move_weights.append([move, weight])

    if can_bear_on(board, player, path, off, roll):
        move_weights.append([['o', 'n'], 5])
    priority = sorted(move_weights, key = itemgetter(1), reverse=True)
    # print(priority)
    # print(priority[0][0])
    return priority[0][0]


def get_playername(player):
    if player == 'B':
        playername = 'black'
    else:
        playername = 'white'
    return playername


def play_again():
    # This function returns True if the player wants to play again, otherwise it returns False.
    print('Do you want to play again? (yes or no)')
    return input().lower().startswith('y')


def show_instructions():
    print('''Instructions:
The Royal Game of Ur is a chase game with 4 safe spaces for each player.  Each player 
starts with 7 markers and the first player to move all of them 17 squares wins.''')
    print()
    print('The board looks like this:')
    inst_board = reset_board()
    draw_board(inst_board)
    input("Press enter to continue")
    print()
    print("""The players (Black and White) start with all of their pieces in reserve, and they bring them onto the 
board by rolling the dice and moving onto their home board. On the following diagram, White's home board
is labeled with Ws and Black's home board is labeled with Bs:""")
    inst_board[0][0] = 'W'
    inst_board[1][0] = 'W'
    inst_board[2][0] = 'W'
    inst_board[3][0] = 'W'
    inst_board[0][2] = 'B'
    inst_board[1][2] = 'B'
    inst_board[2][2] = 'B'
    inst_board[3][2] = 'B'
    draw_board(inst_board)
    input("Press enter to continue")
    print()
    print("White's path around the board looks like this:")
    inst_board = [['↓', '→', ' '], ['←', '→', ' '], ['←', '→', ' '], ['←', '→', ' '], [' ', '→', ' '],
                  [' ', '→', ' '], ['←', '↓', '→'], ['←', '↑', '↑']]
    draw_board(inst_board)
    input("Press enter to continue")
    print()
    print("And Black's path around the board looks like this:")
    inst_board = [[' ', '→', '↑'], [' ', '→', '←'], [' ', '→', '←'], [' ', '→', '←'], [' ', '→', ' '],
                  [' ', '→', ' '], ['→', '↑', '←'], ['↓', '↓', '←']]
    draw_board(inst_board)
    input("Press enter to continue")
    print()
    print("""Players move their pieces by rolling three four-sided dice. There are no numbers on the dice; rather 
they each have two painted corners and two unpainted corners. If a die lands with a painted corner on 
top, it is counted as 1 pip. The roll is the total of pips showing. If no pips are showing, the roll 
is counted as a 4. Practically speaking, each roll of the dice will give a result between 1 and 4.
    
The player then chooses one of their pieces to move and advances it along their path the number of 
squares represented by the dice roll. A piece may not advance if the square it would land on is 
occupied by another piece of the same color. If a piece lands on a square with a rosette on it 
(represented by an R), that player rolls again. The player may choose to move a different piece 
with their additional roll.
    
Here, Black has rolled a 2. The piece at 1,2 may not advance, since the piece at 3,2 is blocking it. 
The piece at 3,2 may advance to 5,2. If Black had thrown a 3, both pieces could move, but the piece 
at 1,2 would land on a rosette at 4,2 and Black would roll again:""")
    inst_board = [[' ', 'B', '↑'], [' ', '→', '←'], [' ', 'B', '←'], [' ', '→', '←'], [' ', '→', ' '],
                  [' ', '→', ' '], ['→', '↑', '←'], ['↓', '↓', '←']]
    draw_board(inst_board)
    input("Press enter to continue")
    print()
    print("""However, The Royal Game of Ur is also a fighting game, so any legal move that lands on an opponent's 
piece will remove the opponent's piece from the board and place it back in the opponent's reserve. 
As 75% of the squares on the board are shared by both paths, there is plenty of contested territory 
to consider.
    
Here, White has rolled a 3. Moving from 7,2 to 8,2 will hit the Black player's piece and send it back to the
Black player's reserve.
Before:""")
    inst_board = [['↓', '→', ' '], ['←', '→', ' '], ['←', '→', ' '], ['←', '→', ' '], [' ', '→', ' '],
                  [' ', '→', ' '], ['←', 'W', '→'], ['←', 'B', '↑']]
    draw_board(inst_board)
    print("\nAfter:")
    inst_board = [['↓', '→', ' '], ['←', '→', ' '], ['←', '→', ' '], ['←', '→', ' '], [' ', '→', ' '],
                  [' ', '→', ' '], ['←', '↓', '→'], ['←', 'W', '↑']]
    draw_board(inst_board)
    input("Press enter to continue")
    print()
    print('''A player may place a piece from their reserve on the board (also known as "bearing on") if the appropriate 
square in their home board is unoccupied. This can happen at any time in the game. If not hit, a piece will 
advance along its entire path until it is removed from the end of the path ("bearing off"). A piece may only
be borne off on an exact roll, so the White player may bear off the piece on the board above only with a 
roll of 3. If White rolls a 4, they must look to make their move elsewhere on the board.
    
If a player may make a move, then the player must make a move.  If the player cannot move due to being blocked
or being unable to bear off, their turn is skipped.''')
    input("Press enter to continue")
    print()
    inst_board = reset_board()
    draw_board(inst_board)
    print("""You will choose to play in one-player or two-player mode.  In two-player mode, the computer will choose
a color to go first and then roll the dice for that player. In one-player mode, you will be asked to choose 
a color, and then one color will be randomly selected to go first. On an empty board, the only available 
first move is to bear on, and the computer will automatically make this move, as it will any time there is 
only one move available for a roll.  If a player wants to bear on with a roll, they should type 'on' when 
asked for their move.  If a player wishes to advance a piece already on the board, they will type the current 
coordinates of that piece in XY fashion. The rosette space near the upper-right corner of the above board is 
at 7,1 and a player who wished to move a piece on that space would type '71'. After every turn, the game board 
will be displayed with a count of each player's pieces borne off and in reserve.
    
Good luck!""")
    print()


print('Welcome to The Royal Game of Ur!')
print()
if input('Would you like to view the instructions? (yes/no) ').lower().startswith('y'):
    show_instructions()
if input('Would you like to view the credits and game notes? (yes/no) ').lower().startswith('y'):
    show_notes()
if input('Would you like to play against the computer? (yes/no): ').lower().startswith('y'):
    invoke_AI = True
else:
    invoke_AI = False

human = ' '
if invoke_AI == True:
    while human != 'W' and human != 'B':
        human = input("Which color would you like to play as? (W or B): ").upper()
if invoke_AI == True and human == 'B':
    computer = 'W'
elif invoke_AI == True and human == 'W':
    computer = 'B'
else:
    computer = ' '
print()

while True:
    # Reset the board and game.
    main_board = reset_board()
    player = who_goes_first()
    b_off = 0
    w_off = 0
    winner = ''
    land_spot = []
    move = []

    playername = get_playername(player)
    print(playername.capitalize() + ' will go first.')

    while not winner:
        switch_players = False
        draw_ingame_board(main_board, w_off, b_off)
        if player == 'B':
            other_player = 'W'
        else:
            other_player = 'B'
        playername = get_playername(player)
        print(playername.capitalize() + "'s turn.", end = " ")
        if player == human:
            print("Press enter to roll.")
            input()
        else:
            print('The computer is rolling.')

        # roll = dice_roll()
        roll = dice_roll()
        if player == 'B':
            path = black_path()
            off = b_off
        else:
            path = white_path()
            off = w_off

        possible_moves = valid_moves(main_board, off, player, path, roll)
        if len(possible_moves) == 0:
            other_playername = get_playername(other_player)
            print(playername.capitalize() + " rolled a %s. No valid moves for that roll! " % roll +
                    other_playername.capitalize() + "'s turn.")
            switch_players = True
        elif len(possible_moves) == 1:
            # Move is forced
            if possible_moves[0][0] == 'o':
                is_bearing_on(main_board, player, path, roll)
            else:
                move = [possible_moves[0][0], possible_moves[0][1]]
                make_move(main_board, player, path, roll, possible_moves[0][0], possible_moves[0][1])
            print(playername.capitalize() + " rolled a %s. Move is forced." % roll)
        else:
            if player != computer:
                move = get_player_move(main_board, player, path, roll, off)
                if move == 'quit':
                    print("Bye!")
                    sys.exit()  # terminate the program
                if move == 'on':
                    is_bearing_on(main_board, player, path, roll)
                else:
                    make_move(main_board, player, path, roll, move[0], move[1])
            else:
                print(playername.capitalize() + " rolled a %s.  Making computer move." % roll)
                move = get_computer_move(main_board, player, path, roll, w_off, b_off)
                if move[0] == 'o':
                    is_bearing_on(main_board, player, path, roll)
                else:
                    make_move(main_board, player, path, roll, move[0], move[1])
                input("Press enter to continue")
        # Did player bear off?
        if (len(possible_moves) == 1 and possible_moves[0][0] != 'o') or len(possible_moves) != 1:
            if is_bearing_off(path, roll, move[0], move[1]):
                switch_players = True
                if player == 'B':
                    b_off += 1
                else:
                    w_off += 1

                # Has player won?
                if player == 'B' and b_off > 6:
                    winner = 'B'
                elif player == 'W' and w_off > 6:
                    winner = 'W'

        # Whose turn is it now?
        if len(possible_moves) != 0:
            if possible_moves[0][1] == 'n':
                land_spot = path[roll - 1]
            else:
                land_spot = get_landing_square(path, roll, move[0], move[1])
        if switch_players == True:
            player = other_player
        if not is_rosette(land_spot[0], land_spot[1]):
            player = other_player


    # Display the final board and declare a winner.
    if winner == 'W':
        draw_ingame_board(main_board, 7, b_off)
    else:
        draw_ingame_board(main_board, 7, w_off)
    # show_counter_status(main_board, b_off, w_off)
    if winner == 'B':
        playername = 'black'
    else:
        playername = 'white'
    print(playername.capitalize() + ' wins!')

    if not play_again():
        break
