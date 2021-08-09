import sys

import cv2 as cv
# opencv doc : https://docs.opencv.org/4.5.3/index.html

# Performance analysis
from time import time
# Custom librairies
from window_capture import WindowCapture
from vision import Vision
from hsv_filter import HsvFilter
from game_map import Cell, GameMap

# Constants
BLUE_COLOR = (255, 0, 0)
GREEN_COLOR = (0, 255, 0)
RED_COLOR = (0, 0, 255)
WHITE_COLOR = (255, 255, 255)

STAIRS_HSV_FILTER = HsvFilter(3, 63, 41, 19, 159, 211, 0, 0, 0, 0)
WALL_HSV_FILTER = HsvFilter(0, 100, 0, 31, 210, 240, 0, 0, 0, 0)


def main(argv):
    # Classes initialization
    wincap = WindowCapture("Crypt of the NecroDancer")

    vision_downstairs = Vision("img/matchTemplate_needles/cotn_downstairs.png")
    vision_character = Vision("img/matchTemplate_needles/cotn_character.png")
    vision_wall = Vision("img/matchTemplate_needles/cotn_wall.png")
    #vision_wall.init_control_gui()

    game_map = GameMap()

    begin_loop_time = time()
    while(True):
        # Get an updated image of the game
        screenshot = wincap.get_screenshot()
        if len(argv) > 1 and argv[2] == "save":
            cv.imwrite("img/save/raw_image.png", screenshot)

        # Pre-process the image (filter)
        processed_image_for_wall = vision_wall.apply_hsv_filter(screenshot, WALL_HSV_FILTER)

        # Objets detection
        ch_rectangles = vision_character.find(screenshot, 0.50)
        # print("Rectangle character:", ch_rectangles)
        ds_rectangles = vision_downstairs.find(screenshot, 0.50, max_results=15)
        # print("Rectangle downstairs: ", ds_rectangles)
        wa_rectangles = vision_wall.find(processed_image_for_wall, 0.40, max_results=10)

        # Update the game board
        ch_centers = vision_character.get_centers_of_rectangles(ch_rectangles)
        ds_centers = vision_downstairs.get_centers_of_rectangles(ds_rectangles)
        game_map.clearCells()
        game_map.updateCells(ch_centers, Cell.CHARACTER, wincap)
        game_map.updateCells(ds_centers, Cell.DOWNSTAIRS, wincap)

        # DEBUG
        print("\nGame state")
        print(game_map)

        # Draw the detection's result onto the original image
        output_image = vision_downstairs.draw_rectangles(screenshot, ds_rectangles)
        output_image = vision_downstairs.draw_crosshairs(screenshot, ds_centers)
        output_image = vision_character.draw_rectangles(screenshot, ch_rectangles, RED_COLOR)
        output_image = vision_character.draw_crosshairs(screenshot, ch_centers)
        output_image = vision_wall.draw_rectangles(screenshot, wa_rectangles, WHITE_COLOR)

        if len(argv) > 1 and argv[2] == "save":
            cv.imwrite("img/save/analyzed_image.png", output_image)
        # Display the processed image
        #cv.imshow("HSV vision", processed_image)
        # Resize the debug window
        # https://answers.opencv.org/question/84985/resizing-the-output-window-of-imshow-function/
        cv.namedWindow("Matches", cv.WINDOW_NORMAL)
        w, h = wincap.get_game_resolution()
        cv.resizeWindow('Matches', w, h)
        cv.imshow("Matches", output_image)

        # Debug the loop rate
        print("FPS {}".format(1 / (time() - begin_loop_time)))
        begin_loop_time = time()

        # Press 'q' to exit the program
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break

    print("End of program")

if __name__ == "__main__":
    main(sys.argv)