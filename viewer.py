from sys import argv
from time import sleep


def main():
    """
    Main function for the program. Sets it up and then begins the replay of the game file.
    """
    try:
        filename = argv[1]
    except IndexError:
        filename = "default.fen"
    with open(str(filename)) as file:
        for line in file:
            sleep(0.5)
            printBoard(convertBoard(line.split(" ")[0]))


def convertBoard(FEN: str) -> list:
    """
    This function converts a given FEN state into a print-able board.

    :param FEN: This is a string, given in Forsyth-Edwards Notation, that is converted into the board setup.
    :return: Returns a board string list list.
    """
    FEN = FEN.split("\\")
    board = [["", "", "", "", "", "", "", ""],
             ["", "", "", "", "", "", "", ""],
             ["", "", "", "", "", "", "", ""],
             ["", "", "", "", "", "", "", ""],
             ["", "", "", "", "", "", "", ""],
             ["", "", "", "", "", "", "", ""],
             ["", "", "", "", "", "", "", ""],
             ["", "", "", "", "", "", "", ""]]
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
        if spaceNumber == 8:
            spaceNumber = 0
            rowNumber += 1
        board[rowNumber][spaceNumber] = item
        spaceNumber += 1
    return board


def printBoard(board):
    """
    Reads the raw board string list list, then prints a board based on that.

    This sequentially goes through the board provided and formats it in such a way that it looks
    very nice when printed out, using symbols and spacing to produce the final string to print.
    :param board: The board to print, in string list list format. One big list with 8 sub-lists with 8 strings each.
    """
    PREFIX = "‒"
    SUFFIX = "‒"
    drawString = "┌‒―‒┬‒―‒┬‒―‒┬‒―‒┬‒―‒┬‒―‒┬‒―‒┬‒―‒┐\n"
    for row in range(len(board)):
        drawString += "│"
        for space in range(len(board[row])):
            if space != 0:
                drawString += "│"
            drawString += PREFIX + getPrettyPiece(board[row][space]) + SUFFIX
        drawString += "│\n"
        if row != 7:
            drawString += "├‒―‒┼‒―‒┼‒―‒┼‒―‒┼‒―‒┼‒―‒┼‒―‒┼‒―‒┤\n"

    print(drawString + "└‒―‒┴‒―‒┴‒―‒┴‒―‒┴‒―‒┴‒―‒┴‒―‒┴‒―‒┘")


def getPrettyPiece(piece):
    """
    This takes a piece str as input and returns the "pretty" form of it, i.e. as a symbol.

    :param piece: A piece str in my piece format, i.e. "wPn" or "bK"
    :return: The "pretty" version of the input piece.
    """
    prettyPiece = ""
    match piece[0:2]:
        case "bR":
            prettyPiece += "♖"
        case "bN":
            prettyPiece += "♘"
        case "bB":
            prettyPiece += "♗"
        case "bQ":
            prettyPiece += "♕"
        case "bK":
            prettyPiece += "♔"
        case "bP":
            prettyPiece += "♙"
        case "wR":
            prettyPiece += "♜"
        case "wN":
            prettyPiece += "♞"
        case "wB":
            prettyPiece += "♝"
        case "wQ":
            prettyPiece += "♛"
        case "wK":
            prettyPiece += "♚"
        case "wP":
            prettyPiece += "♟"
        case " ":
            prettyPiece += "―"
        case _:
            prettyPiece += "😠"
    return prettyPiece


if __name__ == "__main__":
    main()
