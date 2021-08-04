import cv2 as cv
# opencv doc : https://docs.opencv.org/4.5.3/index.html

# Performance analysis
from time import time
# Custom librairies
from window_capture import WindowCapture
from vision import Vision
from hsv_filter import HsvFilter

# Constants
BLUE_COLOR = (255, 0, 0)
GREEN_COLOR = (0, 255, 0)
RED_COLOR = (0, 0, 255)
WHITE_COLOR = (255, 255, 255)

stairs_hsv_filter = HsvFilter(3, 63, 41, 19, 159, 211, 0, 0, 0, 0)
wall_hsv_filter = HsvFilter(0, 100, 0, 31, 210, 240, 0, 0, 0, 0)

# Classes initialization
wincap = WindowCapture("Crypt of the NecroDancer")

vision_downstairs = Vision("img/matchTemplate_needles/cotn_downstairs.png")
vision_character = Vision("img/matchTemplate_needles/cotn_character.png")
vision_wall = Vision("img/matchTemplate_needles/cotn_wall.png")
#vision_wall.init_control_gui()

begin_loop_time = time()
while(True):
    # Get an updated image of the game
    screenshot = wincap.get_screenshot()

    # Pre-process the image (filter)
    processed_image_for_wall = vision_wall.apply_hsv_filter(screenshot, wall_hsv_filter)

    # Objets detection
    ds_rectangles = vision_downstairs.find(screenshot, 0.50)
    ch_rectangles = vision_character.find(screenshot, 0.50)
    wa_rectangles = vision_wall.find(processed_image_for_wall, 0.40, max_results=20)

    # Draw the detection's result onto the original image
    output_image = vision_downstairs.draw_rectangles(screenshot, ds_rectangles)
    output_image = vision_downstairs.draw_rectangles(screenshot, ch_rectangles, RED_COLOR)
    output_image = vision_downstairs.draw_rectangles(screenshot, wa_rectangles, WHITE_COLOR)

    # # Display the processed image
    #cv.imshow("HSV vision", processed_image)
    cv.imshow("Matches", output_image)

    # Debug the loop rate
    print("FPS {}".format(1 / (time() - begin_loop_time)))
    begin_loop_time = time()

    # Press 'q' to exit the program
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print("End of program")
