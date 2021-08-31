from threading import Thread
from time import time, sleep
from random import randint

# Computer vision: https://docs.opencv.org/4.5.3/index.html
import cv2 as cv
# Keyboard inputs
import pyautogui

# Custom librairies
from window_capture import WindowCapture
from computer_vision.vision import Vision
from computer_vision.detection import Detection
from game_map import Cell, GameMap
from position import Direction, translate, getKey, getDirection
#from bot import CryptBot
from a_star.node import Node
from a_star.path_finder import PathFinder

# Constants
BLUE_COLOR = (255, 0, 0)
GREEN_COLOR = (0, 255, 0)
RED_COLOR = (0, 0, 255)
WHITE_COLOR = (255, 255, 255)

DEBUG = True

is_bot_in_action = False


def bot_actions(game):
    global is_bot_in_action
    choosen_direction = [d.value for d in Direction][randint(0, len(Direction))]
    char_pos = game.getCharacterPosition()
    if game.isInBounds(translate(char_pos, choosen_direction)):
        print(getKey(choosen_direction))
        pyautogui.press(getKey(choosen_direction))
        sleep(2)
    is_bot_in_action = False


def bot_action(game_map):
    global is_bot_in_action
    # Compute the shortest path
    char_pos = game_map.getCharacterPosition()
    stairs_pos = game_map.getStairsPosition()
    if char_pos is None or stairs_pos is None and char_pos != stairs_pos:
        return
    path_finder = PathFinder(game_map.getWidth(), game_map.getHeight())
    path_finder.set_start_end(char_pos, stairs_pos)
    path_finder.solve_astar()
    path = path_finder.get_shortest_path_node_iterator()
    next_node = path[1]
    # Get the direction to go
    new_position = (next_node.x, next_node.y)
    choosen_direction = getDirection(char_pos, new_position)
    # Press the key
    if game_map.isInBounds(translate(char_pos, choosen_direction)):
        pyautogui.press(getKey(choosen_direction))
        sleep(0.5)
    is_bot_in_action = False


def main():
    global is_bot_in_action

    # Classes initialization
    wincap = WindowCapture("Crypt of the NecroDancer")
    detector = Detection()
    game_map = GameMap()
    #bot = CryptBot()

    wincap.start()
    detector.start()
    #bot.start()

    begin_loop_time = time()
    while(True):
        if wincap.screenshot is None:
            continue
        
        detector.update(wincap.screenshot)

        # Update the game board
        ch_centers = Vision.get_centers_of_rectangles(detector.character_rectangles)
        ds_centers = Vision.get_centers_of_rectangles(detector.downstairs_rectangles)
        game_map.clearCells()
        game_map.updateCells(ch_centers, Cell.CHARACTER, wincap)
        game_map.updateCells(ds_centers, Cell.DOWNSTAIRS, wincap)

        # TODO implemente a bot class
        # if not is_bot_in_action:
        #     # print("not in action")
        #     is_bot_in_action = True
        #     t = Thread(target=bot_action, args=(game_map))
        #     t.start()
        bot_action(game_map)

        if DEBUG:
            # DEBUG
            #print("\nGame state")
            #print(game_map)
            # Draw the detection's result onto the original image
            output_image = Vision.draw_rectangles(wincap.screenshot, detector.downstairs_rectangles)
            output_image = Vision.draw_crosshairs(wincap.screenshot, ds_centers)
            output_image = Vision.draw_rectangles(wincap.screenshot, detector.character_rectangles, RED_COLOR)
            output_image = Vision.draw_crosshairs(wincap.screenshot, ch_centers)
            output_image = Vision.draw_rectangles(wincap.screenshot, detector.wall_rectangles, WHITE_COLOR)

            # Display the processed image
            #cv.imshow("HSV vision", processed_image)
            # Resize the debug window
            # https://answers.opencv.org/question/84985/resizing-the-output-window-of-imshow-function/
            cv.namedWindow("Matches", cv.WINDOW_NORMAL)
            w, h = wincap.get_game_resolution()
            cv.resizeWindow('Matches', w, h)
            cv.imshow("Matches", output_image)

            # Debug the loop rate
            #print("FPS {}".format(1 / (time() - begin_loop_time)))
            begin_loop_time = time()

        # Press 'q' to exit the program
        if cv.waitKey(1) == ord('q'):
            detector.stop()
            wincap.stop()
            #bot.stop()
            cv.destroyAllWindows()
            break

    print("End of program")

if __name__ == "__main__":
    main()