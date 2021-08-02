import cv2 as cv
# opencv doc : https://docs.opencv.org/4.5.3/index.html

# Performance analysis
from time import time

from window_capture import WindowCapture
from vision import Vision

wincap = WindowCapture("Crypt of the NecroDancer")
vision_downstairs = Vision("img/cotn_downstairs.png")

begin_loop_time = time()
while(True):
    # Get an updated image of the game
    screenshot = wincap.get_screenshot()

    # Display the processed image
    points = vision_downstairs.find(screenshot, 0.5, 'rectangles')

    # Debug the loop rate
    print("FPS {}".format(1 / (time() - begin_loop_time)))
    begin_loop_time = time()

    # Press 'q' to exit the program
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print("End of program")
