from enum import Enum

from numpy import broadcast

class Cell(Enum):
    EMPTY = " "
    CHARACTER = "C"
    DOWNSTAIRS = "D"
    WALL = "W"
    ENEMY = "E"

CELL_TO_STR = {}
CELL_TO_STR[Cell.EMPTY] = ' '
CELL_TO_STR[Cell.CHARACTER] = 'Ϙ'
CELL_TO_STR[Cell.DOWNSTAIRS] = 'X'      # Ϟ
CELL_TO_STR[Cell.WALL] = 'Π'
CELL_TO_STR[Cell.ENEMY] = 'O'           # Ω

GAME_MAP_WIDTH_IN_CELLS = 27
GAME_MAP_HEIGHT_IN_CELLS = 14

class GameMap:
    width = 0
    height = 0
    board = None


    def __init__(self, width=GAME_MAP_WIDTH_IN_CELLS, height=GAME_MAP_HEIGHT_IN_CELLS):
        self.width = width
        self.height = height
        self.clearCells()

    
    def __str__(self):
        result = "(" + str(self.width) + "," + str(self.height) + ")\n"
        result += "  "
        for _ in range(6):
            result += " "
        result += "⑤"
        for _ in range(4):
            result += " "
        result += "⑩"
        for _ in range(4):
            result += " "
        result += "⑮"
        for _ in range(4):
            result += " "
        result += "⑳"
        for _ in range(4):
            result += " "
        result += "㏸\n"
        result += "  +"
        for _ in range(self.width):
            result += "-"
        result += "+\n"
        for y in range(self.height):
            result += "{:02d}".format(y) + "|"
            for x in range(self.width):
                result += CELL_TO_STR[self.board[y][x]]
            result += "|\n"
        result += "  +"
        for _ in range(self.width):
            result += "-"
        result += "+"
        return result


    # Return the Cell at the position, a (x, y) tuple
    def getCell(self, position):
        return self.board[position[1]][position[0]]


    def setCell(self, position, cell):
        self.board[position[1]][position[0]] = cell


    '''Convert the position of a pixel in a game screenshot to a cell position representing the game
    @param pixel_position a (x, y) tuple
    @param game_sizes a (width, height) tuple
    '''
    def convertPixelPositionToCellPosition(self, pixel_position, game_resolution):
        cell_width = int(game_resolution[0] / self.width)
        cell_height = int(game_resolution[1] / self.height)
        x_cell = int(pixel_position[0] / cell_width)
        y_cell = int(pixel_position[1] / cell_height)
        return (x_cell, y_cell) 

    # Set the content of all cells at Cell.EMPTY
    def clearCells(self):
        # self.board = [[Cell.EMPTY] * self.width] * self.height
        self.board = []
        for y in range(self.height):
            self.board.append([])
            for _ in range(self.width):
                self.board[y].append(Cell.EMPTY)

    '''Set the cell with cell_content at the centers' positions
    @param centers, a list of position (x, y) tuple, x and y in pixel of the screen
    @param cell_content, a element of the Cell enum
    @param window_capture, the window_capture instance from which the centers have been found
    '''
    def updateCells(self, centers, cell_content, window_capture):
        for center in centers:
            game_resolution = window_capture.get_game_resolution()
            cell_pos = self.convertPixelPositionToCellPosition(center, game_resolution)
            self.setCell(cell_pos, cell_content)
