from sys import exit, argv
from stockfish import Stockfish
from time import sleep
from halo import Halo
from random import randint
from shutil import get_terminal_size
from datetime import datetime
from platform import system, machine
from pyinputplus import inputStr, inputMenu
from re import match

"""
- MacOS support
- Handle 50-Half-move rule
- Convert pieces to standard notation internally.
- Convert all "do" statements into statements that also return T/F based on success
"""

# This turns the game into full-auto high speed mode. It's not useful now but it was very useful while testing so I
# didn't have to play. Yes, it really is that simple. YES, it is really THAT simple.
debugGame = False
stockfish = None

# This allows me to determine who is trying to use this program.
match system():
    case "Windows":
        # noinspection PyRedeclaration
        stockfish = Stockfish("stockfish_WIN.exe")
    case "Linux":
        # noinspection PyRedeclaration
        stockfish = Stockfish("stockfish_NIX")
    case "Darwin":
        if machine() == "arm64":
            stockfish = Stockfish("stockfish_MAC_ARM64")
        elif machine() == "powerpc":
            print("MacOS on PowerPC is not supported! How did you even install python 3.10 on PowerPC?")
            exit()
        else:
            stockfish = Stockfish("stockfish_MAC")
    case _:
        print(system(), "on", machine(), "is not a supported OS!")
        exit()

# Will this ever exit beta? No.
print("Amelia's Chess Program b0.2 running on", system(), "on", machine())
print("Stockfish", stockfish.get_stockfish_major_version(), "loaded!")

# Baby's first chess game
stockfish.set_elo_rating(1400)


class ChessBoard:
    def __init__(self, arrangement=None):
        if not arrangement:
            # This was originally wrong! Turns out I had everything flipped. Yes I know there are more
            # standard ways to notate what piece goes where, and that actually would work out fine now,
            # but I needed to do it this way originally, and so, it stuck.
            self.arrangement = [
                ["bRn", "bN", "bB", "bQ", "bKn", "bB", "bN", "bRn"],
                ["bPn", "bPn", "bPn", "bPn", "bPn", "bPn", "bPn", "bPn"],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                ["wPn", "wPn", "wPn", "wPn", "wPn", "wPn", "wPn", "wPn"],
                ["wRn", "wN", "wB", "wQ", "wKn", "wB", "wN", "wRn"]
            ]
        else:
            self.arrangement = arrangement

    def __iter__(self):
        return iter(self.arrangement)

    def __next__(self):
        return next(self.arrangement)

    def __str__(self):
        PREFIX = "‒"
        SUFFIX = "‒"
        # One of the few cases of consts in my program. Future releases will have more.
        drawString = "┌‒―‒┬‒―‒┬‒―‒┬‒―‒┬‒―‒┬‒―‒┬‒―‒┬‒―‒┐\n"
        # I don't know if I have mentioned this enough: you have no idea the scale of operation I had to undertake to
        # make this board even look as good as it does. And it doesn't even look that good.
        for row in range(len(self.arrangement)):
            drawString += "│"
            for space in range(len(self.arrangement[row])):
                if space != 0:
                    drawString += "│"
                match self.arrangement[row][space][0:2]:
                    case "bR":
                        drawString += PREFIX + "♖" + SUFFIX
                    case "bN":
                        drawString += PREFIX + "♘" + SUFFIX
                    case "bB":
                        drawString += PREFIX + "♗" + SUFFIX
                    case "bQ":
                        drawString += PREFIX + "♕" + SUFFIX
                    case "bK":
                        drawString += PREFIX + "♔" + SUFFIX
                    case "bP":
                        drawString += PREFIX + "♙" + SUFFIX
                    case "wR":
                        drawString += PREFIX + "♜" + SUFFIX
                    case "wN":
                        drawString += PREFIX + "♞" + SUFFIX
                    case "wB":
                        drawString += PREFIX + "♝" + SUFFIX
                    case "wQ":
                        drawString += PREFIX + "♛" + SUFFIX
                    case "wK":
                        drawString += PREFIX + "♚" + SUFFIX
                    case "wP":
                        drawString += PREFIX + "♟" + SUFFIX
                    case " ":
                        drawString += PREFIX + "―" + SUFFIX
                    case _:
                        # This shouldn't happen unless something very wrong happens.
                        drawString += PREFIX + "😠" + SUFFIX
            drawString += "│\n"
            if row != 7:
                drawString += "├‒―‒┼‒―‒┼‒―‒┼‒―‒┼‒―‒┼‒―‒┼‒―‒┼‒―‒┤\n"
        return drawString + "└‒―‒┴‒―‒┴‒―‒┴‒―‒┴‒―‒┴‒―‒┴‒―‒┴‒―‒┘"

    def __cmp__(self, other):
        if self.arrangement == other.arrangement:
            return True
        else:
            return False

    def __getitem__(self, item):
        pos0 = getIndexFromPos(item)[0]
        pos1 = getIndexFromPos(item)[1]
        if 0 <= pos0 <= 7:
            if 0 <= pos1 <= 7:
                return self.arrangement[pos1][pos0]
            elif pos1 < 0:
                return self.arrangement[0][pos0]
            elif pos1 > 7:
                return self.arrangement[7][pos0]
            else:
                return None
        elif pos0 < 0:
            if 0 <= pos1 <= 7:
                return self.arrangement[pos1][0]
            elif pos1 < 0:
                return self.arrangement[0][0]
            elif pos1 > 7:
                return self.arrangement[7][0]
            else:
                return None
        elif pos0 > 7:
            if 0 <= pos1 <= 7:
                return self.arrangement[pos1][7]
            elif pos1 < 0:
                return self.arrangement[0][7]
            elif pos1 > 7:
                return self.arrangement[7][7]
            else:
                return None
        else:
            return None

    def __setitem__(self, key, value):
        pos = getIndexFromPos(key)
        self.arrangement[pos[1]][pos[0]] = value

    def __delitem__(self, key):
        pos = getIndexFromPos(key)
        self.arrangement[pos[1]][pos[0]] = " "

    def __contains__(self, item):
        for row in self.arrangement:
            for square in self.arrangement[row]:
                if square == item:
                    return True
        return False

    def __len__(self):
        return len(self.arrangement)

    def __eq__(self, other):
        if self.arrangement == other.arrangement:
            return True
        else:
            return False

    def __ne__(self, other):
        if self.arrangement != other.arrangement:
            return True
        else:
            return False

    def importFEN(self, FEN):
        global moveNumber, activeColor, enPassantTarget
        # This block of code, unlike it's sister getFENfromState() is actually a little bit ugly. (A lot).
        # It DOES work, which is really nice. More to follow.
        args = FEN.split(" ")[1:]
        # args becomes the part of the FEN that isn't the literal board definition.
        # Splitting it like this makes it nicer.
        activeColor = args[0]
        enPassantTarget = args[2]
        moveNumber = int(args[4])
        FEN = FEN.split(" ")[0].split("\\")
        # Originally this line was "FEN = FEN.split("\\") and that actually worked fine, but I wanted to make sure that
        # the extra data wasn't accidentally used in some way, even though I don't think that could even happen.
        data = []
        for line in range(len(FEN)):
            for char in range(len(FEN[line])):
                match FEN[line][char]:
                    case "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8":
                        for uselessVariable in range(0, int(FEN[line][char])):
                            data.append(" ")
                    case "p":
                        data.append("bP")
                    case "P":
                        data.append("wP")
                    case "k":
                        data.append("bK")
                    case "K":
                        data.append("wK")
                    case "q":
                        data.append("bQ")
                    case "Q":
                        data.append("wQ")
                    case "r":
                        data.append("bR")
                    case "R":
                        data.append("wR")
                    case "n":
                        data.append("bN")
                    case "N":
                        data.append("wN")
                    case "b":
                        data.append("bB")
                    case "B":
                        data.append("wB")
        spaceNumber = 0
        rowNumber = 0
        for item in data:
            # This isn't the way I wanted to do this originally, but
            # appending the spaces directly in the code above didn't
            # work for reasons I still do not understand fully.
            if spaceNumber == 8:
                spaceNumber = 0
                rowNumber += 1
            self.arrangement[rowNumber][spaceNumber] = item
            spaceNumber += 1
        for castleType in args[1]:
            # Even though stockfish doesn't care, it is still relevant
            # information, so the proper piece labels are set here
            # for castling.
            match castleType:
                case "-":
                    pass
                case "k":
                    self.arrangement["E8"] = "bKn"
                    self.arrangement["H8"] = "bRn"
                case "q":
                    self.arrangement["E8"] = "bKn"
                    self.arrangement["A8"] = "bRn"
                case "W":
                    self.arrangement["E1"] = "wKn"
                    self.arrangement["H1"] = "wRn"
                case "Q":
                    self.arrangement["E1"] = "wKn"
                    self.arrangement["A1"] = "wRn"

    def exportFEN(self):
        FEN = ""
        blankCount = 0
        # I am actually pretty proud of how quickly I got this to work. When I first learned about Forsyth-Edwards
        # notation, I thought it was incredibly daunting. Fortunately for me, I got it working pretty much on my first
        # try. The little bit at the end that indicate some extra stuff like castling and whatever came later, but that
        # was actually fairly easy to do. The hard part was definitely the rendering of the main board state.
        for row in range(len(self.arrangement)):
            for square in range(len(self.arrangement[row])):
                # This bit of code ^ appears often. It is (I think) the easiest way to address
                # my board storage method as a sequence of spaces. I really doubt it's the fastest way
                # but the shield of "It's python who cares about efficiency" really protects me from anything.
                if self.arrangement[row][square] != " ":
                    if blankCount > 0:
                        FEN += str(blankCount)
                        blankCount = 0
                    match self.arrangement[row][square]:
                        # I love python3.10 and match/case. It really makes this so much nicer than it could be.
                        case "wP" | "wPn" | "wPe":
                            FEN += "P"
                        case "wR" | "wRn":
                            FEN += "R"
                        case "wN":
                            FEN += "N"
                        case "wB":
                            FEN += "B"
                        case "wQ":
                            FEN += "Q"
                        case "wK" | "wKn":
                            # All the types of pawns/kings/whatever get truncated because stockfish does not care.
                            FEN += "K"
                        case "bP" | "bPn" | "bPe":
                            FEN += "p"
                        case "bR" | "bRn":
                            FEN += "r"
                        case "bN":
                            FEN += "n"
                        case "bB":
                            FEN += "b"
                        case "bQ":
                            FEN += "q"
                        case "bK" | "bKn":
                            FEN += "k"
                elif self.arrangement[row][square] == " ":
                    blankCount += 1
            if blankCount > 0:
                FEN += str(blankCount)
                blankCount = 0
            if row != len(self.arrangement) - 1:
                # Adding the / between rows. Trivial!
                FEN += "/"
        FEN += (
                " " + activeColor + " " + getCastles() + " " + getEnPassant().lower() + " 0 " + str(moveNumber))
        # The " 0 " represents the status of the 50 move rule. I don't care about nerd rules so this is ignored.
        # This choice certainly will have consequences that I also do not care about.
        return FEN


# Important notes about piece standards: first letter should always be lower-case, and represents the color of the
# piece. "w" for white, "b" for black, and " " for empty space. The second letter indicates the type of piece and
# is always capitalized. The optional third letter indicates the piece's state, "n" meaning "piece has not yet moved"
# which is used for castling and pawn's double-move. "e" means "this piece can be captured in en-passant".
# This likely could have been done a little bit more chess-standard "b for black bishop, B for white bishop" but the
# way that I did it here made it easy to visualise the pieces as I was writing the program.

# General housekeeping. Setting things up fresh.
moveNumber = 0
activeColor = "w"
enPassantTarget = ""
isEnPassantCapture = False
board = ChessBoard()


def main():
    """
    Main function of the program. Sets up thr program and then begins a game loop.

    Either sets up the game as a new game, or loads data from a save game submitted
    via python arguments. Save files are stored as .FEN files, and are just text files
    containing a sequence of FEN positions, separated by newlines.
    """
    global activeColor, moveNumber
    # Pulling in activeColor and moveNumber here so that we can use them later just in case we are loading from file
    gameRunning = True
    firstMove = True
    # Setting the game up. This makes sure that a bit of housekeeping can occur right at the start. It specifically
    # prevents you from accidentally appending an extra line to a save file upon loading, but also prevents the
    # newlines from being spawned.
    filename = datetime.now().strftime("saves/Game played on %B %d, %Y at %Hh%Mm%Ss.fen")
    # Creates a default save file name. This gets overwritten by the next block of code if an argument is passed to
    # chess.py indicating a save file that should be loaded, and, if so, the file is loaded as the in-use save file,
    # and used to determine how to set up the starting board
    try:
        if argv[1]:
            with open(argv[1]) as file:
                finalLine = ""
                for line in file:
                    # Literally just overwriting the same var until the EOF. This has the same effect as doing file[-1]
                    # except it's way slower than that would be. Thankfully for me, it isn't a thing, so my method is
                    # fast enough. :)
                    finalLine = line
                if match(r'^(((?:[rnbqkpRNBQKP1-8]+/){7})[rnbqkpRNBQKP1-8]+)\s([b|w])\s(-|[KQkq]{1,4})\s(-|[a-h]['r'1'
                         r'-8])\s(\d+\s\d+)$', finalLine):
                    filename = argv[1]
                    board.importFEN(finalLine)
                else:
                    print("The requested file is invalid! Starting new game.")
    except IndexError:
        # This is kind of a clunky way of doing it but I couldn't think up any other ways to do it. So enjoy.
        pass
    while gameRunning:
        # Main game loop starts here. Everything else was setup.
        sleep(0.5)
        # A little bit of delay, for spicy effect.
        doPromotePawns()
        # Checking if any pawns are due for promotion, then promoting them.
        if firstMove:
            try:
                if not argv[1]:
                    with open(filename, "a") as file:
                        # As mentioned before, this prevents a bug wherein an extra line is added to the save file.
                        file.write(board.exportFEN() + "\n")
            except IndexError:
                pass
            firstMove = not firstMove
        else:
            with open(filename, "a") as file:
                file.write(board.exportFEN() + "\n")
            print("\n" * get_terminal_size().lines, end='')
            # This prints like 80 lines.
        print(board)
        # You have NO idea how long it took me to make the board look nice.
        if activeColor == "w":
            # Player move. Note the inconsistent use of "w" vs "white" in this program. Bathe in it.
            doCheckForMate()
            if debugGame:
                # Yes, it really is this simple.
                doComputerMove()
            else:
                doPlayerMove()
            doCheckForMate()
            # Check draws before mates to prioritize sadness
            doClearEnPassant("b")
            # Again, I'm sure there's a better way to do this, but whatever.
            activeColor = "b"
        else:
            # TODO: Note #1: doCheckForMate() is not working for unknown reasons. Check in on that.
            doCheckForMate()
            doComputerMove()
            doCheckForMate()
            doClearEnPassant("w")
            moveNumber += 1
            # Chess fact: The move number increments at the end of black's turn.
            activeColor = "w"


def doPlayerMove():
    """
    This function is responsible for the player's (white's) move.
    It takes user input, sanitizes it, and then validates it.
    Once it is validated, the move is made and the loop ends.
    """
    while True:
        # I have broken my streak of break-less loops :(
        userMove = inputStr("What move would you like to make?")
        if match(r"^([a-hA-H])([1-8])([a-hA-H])([1-8])$", userMove):
            # This checks for a standard move in algebraic notation. i.e. a2a4
            stockfish.set_fen_position(board.exportFEN())
            # I know this is cheating, but it also cut the size of this program in half!
            if stockfish.is_move_correct(userMove):
                # At this point the move is sanitized enough to just willy-nilly grab data by index
                doMovePiece(userMove[0:2].upper(), userMove[2:4].upper())
                break
            else:
                print("Move", board[userMove[0:2].upper()][0:1], "to", userMove[2:4].upper(),
                      "is invalid!")
        elif userMove == "castle":
            if doCastle("white"):
                # doCastle() actually does return true or false to
                # determine if it failed or not, despite being a "do" func
                break
        elif userMove == "exit":
            # HCF
            exit()
        else:
            # Wording is confusing here. Maybe "That is not a valid input"
            print("That is not a valid input!")


def doComputerMove():
    """
    This function is responsible for the computer's (black's) move.
    It begins by pretending to actually think about the move, then
    it asks stockfish to make the best move, which it does pretty
    much instantly. And because computers are nice to me, I don't
    need to sanitize the input at all.
    """
    if debugGame:
        pass
    else:
        # Just for fun.
        # Halo is so nice.
        spinner = Halo(text='Computer deciding...', spinner='dots')
        spinner.start()
        sleep(randint(2, 5))
        spinner.stop()
    stockfish.set_fen_position(board.exportFEN())
    # Computers are so nice. No input validation needed.
    idealMove = stockfish.get_best_move()
    match idealMove:
        case "O-O":
            doCastle("O-O")
        case "O-O-O":
            doCastle("O-O-O")
        case _:
            doMovePiece(idealMove[0:2].upper(), idealMove[2:4].upper())


def doEndGame(loser: str):
    """
    This function ends the game. It is very simple.

    :param loser: This parameter determines which player is the loser, and
        then selects the correct outcome based on that.
    """
    match loser:
        # This does not need to be a function, but I am sentimental.
        case "white":
            # 🥳🥳🥳
            print("Black wins!")
        case "black":
            # 🥳🥳🥳
            print("White wins!")
        case "draw":
            # 🥳🥳🥳🥳
            print("Draw!")
    exit()


def doMovePiece(fromPos: str, toPos: str):
    """
    Moves a piece from one location to another. Can be used to capture pieces.

    This function moves pieces around, and does a little bit of behind-the-scenes work, like marking pieces for
    en passant, along with castling nonsense. Assuming all else is well, the piece in question is moved.
    :param fromPos: The starting position of the piece, in half-algebraic format, i.e. "A2" or "B7"
    :param toPos: The target position of the piece, in half-algebraic format, i.e. "A2" or "B7"
    """
    # The way I check for en passant is very stupid! It works!
    global isEnPassantCapture
    piece = board[fromPos]
    ctpos = getIndexFromPos(toPos)
    # "ctpos" means "converted toPos". Clear, right?
    try:
        if piece[2] == "n" and piece[1] == "P" and (
                int(fromPos[1]) - 2 == int(toPos[1]) or int(fromPos[1]) + 2 == int(toPos[1])):
            board[fromPos] = piece[0] + piece[1] + "e"
        elif piece[2] == "n" and piece[1] == "P" and (
                int(fromPos[1]) - 1 == int(toPos[1]) or int(fromPos[1]) + 1 == int(toPos[1])):
            board[fromPos] = piece[0] + piece[1]
        elif piece[2] == "n" and piece[1] == "K":
            board[fromPos] = piece[0] + piece[1]
        elif piece[2] == "n" and piece[1] == "R":
            board[fromPos] = piece[0] + piece[1]
        elif piece[2] == "e" and piece[1] == "P":
            board[fromPos] = piece[0] + piece[1]
        piece = board[fromPos]
    except IndexError:
        # I am certain there is a less awful way to do this.
        pass
    board[fromPos] = " "
    board[toPos] = piece
    if isEnPassantCapture:
        board.arrangement[ctpos[1]][ctpos[0] + 1] = " "
        # Doesn't even use doSetPiece. Just eliminates it like it is nothing. Really messed up.
        isEnPassantCapture = False


def doCheckForMate():
    """
    This function determines if a given board position is in a game-ending state.

    This function asks stockfish to observe the board, and if it is unable to determine any moves to be made, then
    the game is over, depending on who made the last move, the game is handed to the winner. There is a non-zero
    chance that some draws are marked as wins for one player or another. I could not find a solution for this issue.
    """
    # The urge to call this "checkMate()" and break convention was ENORMOUS.
    # TODO: This does not work for some unknown reason. See note #1 above
    if len(stockfish.get_top_moves()) == 0:
        if activeColor == "b":
            stockfish.set_fen_position(board.exportFEN().split(" ", 2)[0]+" w "+board.exportFEN().split(" ", 2)[2])
            if len(stockfish.get_top_moves()) == 0:
                doEndGame("draw")
            else:
                doEndGame("black")
        elif activeColor == "w":
            stockfish.set_fen_position(board.exportFEN().split(" ", 2)[0] + " b " + board.exportFEN().split(" ", 2)[2])
            if len(stockfish.get_top_moves()) == 0:
                doEndGame("draw")
            else:
                doEndGame("white")


def doPromotePawns():
    """
    This function goes through the board square by square and promotes any pawns that need promoting.
    """
    # You might be inclined to think that this could have been made even faster.
    # Then, you remember it is written in python so it doesn't matter anyways.
    # TODO: This does not currently work. Might be best to move this into the board class.
    for row in range(len(board.arrangement)):
        for square in range(len(board.arrangement[row])):
            if board.arrangement[row][square] == "bP":
                if square == 7:
                    board.arrangement[row][square] = "bQ"
            elif board.arrangement[row][square] == "wP":
                if square == 0:
                    board.arrangement[row][square] = "wQ"


def doClearEnPassant(color: str):
    """
    This function goes through the board square by square and clears en passant status from any pawns that have it.

    :param color: This parameter determines which color of pawns should be cleared. This will either be "w" or "b"
    """
    for square in board:
        if square == color + "Pe":
            # Remove their e's
            board[square] = color + "P"


def doCastle(side: str) -> bool:
    """
    This function performs the actual castling operation, determining the validity based on getCastles()

    For white castling, we need to do a bit of sanitization and validity checking. For black, no
    nonsense is required.
    :param side: This is the type castle the program will execute. "white" requires validation, anything else does not.
    :return: Returns a boolean representing the success of castling. If it succeeds, then it returns True.
    """
    if side == "white":
        # This is a pretty simple maneuver given that I already have getCastles(). It's basically just checking for
        # all the possible configurations and then pushing it from there.
        castles = getCastles()
        if ("K" in castles) and ("Q" in castles):
            while True:
                choice = inputMenu(["King", "Queen"], "Castle on King's side or Queen's side?\n").upper()
                # The parenthesis around the letters indicates the letters that the player should send
                if choice[0] == "K":
                    # Chess fact: This is the best way to do this.
                    doMovePiece("H1", "F1")
                    doMovePiece("E1", "G1")
                    return True
                elif choice[0] == "Q":
                    doMovePiece("A1", "D1")
                    doMovePiece("E1", "C1")
                    return True
        elif "K" in castles and "Q" not in castles:
            doMovePiece("H1", "F1")
            doMovePiece("E1", "G1")
            return True
        elif "Q" in castles and "K" not in castles:
            doMovePiece("A1", "D1")
            doMovePiece("E1", "C1")
            return True
        else:
            print("You cannot castle at this time!")
            return False
    else:
        # O-O and O-O-O are chess notation for castling. Again, as above, I have no idea if this code actually runs
        # because it appears that stockfish will never attempt to castle. I tested it vigorously, The code remains here
        # just in case I didn't test all possible scenarios.
        if side == "O-O":
            doMovePiece("H8", "F8")
            doMovePiece("E8", "G8")
            return True
        elif side == "O-O-O":
            doMovePiece("A8", "D8")
            doMovePiece("E8", "C8")
            return True


def getIndexFromPos(pos: str) -> list:
    """
    Converts a position str into an position index list.

    Takes a position, given in half-algebraic notation, i.e. "A2" or "B7"
    and returns the board index position, i.e. "[0, 4]" or "[3, 6]"
    :param pos: The position to convert
    :return: The index of the position, in the form of a list of ints.
    """
    # I am sure this can be done in a better way. It's just the first thing I thought of.
    vertDict = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    horizDict = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
    # I was a bit mean to myself, I think this is a fine way of doing this. Just wish there was some way to return
    # the two index values in a way that made them easier to use, because right now you have to do like
    # gameState[getIndexFromPos[0]][getIndexFromPos[1]] to set a board position directly and I just think
    # it looks a bit worse than it could.
    return [horizDict.get(pos[0]), vertDict.get(pos[1])]


def getEnPassant() -> str:
    """
    Scrolls through the board square by square and finds an en passant-able pawn, and then returns it's location.

    :return: Either returns a board position (of the en passant-able pawn) or "-" if there are none present.
    """
    for square in board:
        if square == "bPe" or square == "wPe":
            # Unbelievably, my forward thinking piece notation method actually saved me an immense amount of time
            # here! I was really lost for plan when designing this originally.
            return square.pos
    return "-"


def getCastles() -> str:
    """
    This function scrolls through the board square by square and determines if there are any valid castle moves.

    :return: A list of castles that are valid, in FEN (i.e "KQkq" for all possible castles) or "-" for no valid castles.
    """
    castles = ""
    # Much as doCastle() arbitrarily sets pieces, getCastles() arbitrarily reads pieces. I think this is fine.

    if board["E1"] == "wKn" and board["F1"] == " " and board["G1"] == " " and board["H1"] == "wRn":
        castles += "K"
    if board["A1"] == "wRn" and board["B1"] == " " and board["C1"] == " " \
            and board["D1"] == " " and board["E1"] == "wKn":
        castles += "Q"
    if board["E8"] == "bKn" and board["F8"] == " " and board["G8"] == " " and board["H8"] == "bRn":
        castles += "k"
    if board["A8"] == "bRn" and board["B8"] == " " and board["C8"] == " " \
            and board["D8"] == " " and board["E8"] == "bKn":
        castles += "q"
    if castles == "":
        castles = "-"
    return castles


if __name__ == "__main__":
    main()
else:
    exit()
