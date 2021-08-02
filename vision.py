import numpy as np
import cv2 as cv
# opencv doc : https://docs.opencv.org/4.5.3/index.html

class Vision:
    # Attributs
    needle_img = None
    needle_width = 0
    needle_height = 0
    method = None

    # Constructor
    def __init__(self, needle_img_path, method=cv.TM_CCOEFF_NORMED):
        # Load the image we are trying to match
        # https://docs.opencv.org/4.5.3/df/dfb/group__imgproc__object.html
        self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)

        # Save the dimension of the needle image
        self.needle_width = self.needle_img.shape[1]
        self.needle_height = self.needle_img.shape[0]

        # There are 6 methods to choose from:
        # TM_SQDIFF, TM_SQDIFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_CCOEFF, TM_CCOEFF_NORMED
        self.method = method

    def find(self, haystack_img, threshold=0.5, debug_mode=None):
        # Run the OpenCV Algorithm
        result = cv.matchTemplate(haystack_img, self.needle_img, self.method)

        # Get all the positions from the match result that exceed our threshold
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))

        # You will notice a lot of overlapping rectangles get drawn.
        # We can eliminate those redundant locations by using groupRectangles
        # Format the location in a list of [x, y, w, h] rectangles
        rectangles = list()
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_width, self.needle_height]
            # Add every box to the list twice in order to retain single (non-overlapping) boxes
            if len(rectangles) == 1:
                rectangles.append(rect)
            rectangles.append(rect)

        # Apply group rectangles
        # The groupThreshold parameter should usually be 1.
        # If you put it at 0 then no grouping is done.
        # If you put it at 2 then an object needs at least 3 overlapping rectangles to appear in the result
        # I have set eps to 0.5 which is :
        # "Relative difference between sides of the rectangles to merge them into a group"
        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
        
        points = []

        if len(rectangles):
            line_color = (0, 255, 0)
            line_type = cv.LINE_4
            marker_color = (255, 0, 255)
            marker_type = cv.MARKER_CROSS

            # Loop over all the locations and draw their rectangle
            for (x, y, w, h) in rectangles:

                # Determine the center position
                center_x = x + int(w/2)
                center_y = y + int(h/2)
                # Save the points
                points.append((center_x, center_y))

                if debug_mode == 'rectangles':
                    # Determine the box positions
                    top_left = (x, y)
                    bottom_right = (x + w, y + h)
                    # Draw the boxes
                    cv.rectangle(haystack_img, top_left, bottom_right, color=line_color, thickness=2, lineType=line_type)
                elif debug_mode == 'points':
                    cv.drawMarker(haystack_img, (center_x, center_y), marker_color, marker_type)

        if debug_mode:
            # h, w = haystack_img.shape[0:2]
            # neww = 800
            # newh = int(neww*(h/w))
            # haystack_img = cv.resize(haystack_img, (neww, newh))  
            cv.imshow('Matches', haystack_img)

        return points

if __name__ == "__main__":
    vision = Vision("img/cotn_downstairs.png")
    points = vision.find("img/cotn_home_2.png", threshold=0.8, debug_mode='rectangles')
    print(points)