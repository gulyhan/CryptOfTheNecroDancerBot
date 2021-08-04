import numpy as np
import cv2 as cv
# opencv doc : https://docs.opencv.org/4.5.3/index.html
from hsv_filter import HsvFilter


class Vision:

    # Constant
    TRACKBAR_WINDOW = "Trackbars"

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


    def find(self, haystack_img, threshold=0.5, max_results=10):
        # Run the OpenCV Algorithm
        result = cv.matchTemplate(haystack_img, self.needle_img, self.method)

        # Get all the positions from the match result that exceed our threshold
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))

        # Reshape a potential empty array (locations) so we can concatenate it with others rectangles
        if not locations:
            return np.array([], dtype=np.int32).reshape(0, 4)

        # You will notice a lot of overlapping rectangles get drawn.
        # We can eliminate those redundant locations by using groupRectangles
        # Format the location in a list of [x, y, w, h] rectangles
        rectangles = []
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

        if len(rectangles) > max_results:
            print("Warning: too many results, raise the threshold")
            rectangles = rectangles[:max_results]

        return rectangles


    '''
        Convert rectangles into a list of [x, y] positions being the center of the rectangles
        @param given a list of [x, y, w, h] rectangles
    '''
    def get_centers_of_rectangles(self, rectangles):
        points = []
        # Loop over all the locations and draw their rectangle
        for (x, y, w, h) in rectangles:
            # Determine the center position
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            # Save the points
            points.append((center_x, center_y))

        return points


    '''
        Return the canvas with the rectangles drawn on it
        @param : rectangles is a list of [x, y, w, h] rectangles
    '''
    def draw_rectangles(self, canvas, rectangles, line_color=None):
        # the BGR color
        if line_color is None:
            line_color = (0, 255, 0)
        line_type = cv.LINE_4

        # Loop over all the locations and draw their rectangle
        for (x, y, w, h) in rectangles:
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            # Draw the boxes
            cv.rectangle(canvas, top_left, bottom_right, color=line_color, thickness=2, lineType=line_type)
            
        return canvas


    '''
        Return the canvas with a crosshair at the points' position
        @param points is a list of [x, y] positions
    '''
    def draw_crosshairs(self, canvas, points):
        # the BGR color
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS

        for (center_x, center_y) in points:
            cv.drawMarker(canvas, (center_x, center_y), marker_color, marker_type)

        return canvas

    # Create a GUI window with controls for adjusting arguments in real time
    def init_control_gui(self):
        cv.namedWindow(self.TRACKBAR_WINDOW, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.TRACKBAR_WINDOW, 350, 750)

        # required callbacks for createTrackbar
        def nothing(position):
            pass
        
        # Create the trackbars for bracketing
        # OpenCV scale for HSV is : H: 0-179, S 0-255, V: 0-255
        cv.createTrackbar("HMin", self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv.createTrackbar("SMin", self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar("VMin", self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar("HMax", self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv.createTrackbar("SMax", self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar("VMax", self.TRACKBAR_WINDOW, 0, 255, nothing)

        # Set the default value for Max HSV trackbars
        cv.setTrackbarPos("HMax", self.TRACKBAR_WINDOW, 179)
        cv.setTrackbarPos("SMax", self.TRACKBAR_WINDOW, 255)
        cv.setTrackbarPos("VMax", self.TRACKBAR_WINDOW, 255)

        # Trackbars for increasing or decreasing saturation and value
        cv.createTrackbar("SAdd", self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar("SSub", self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar("VAdd", self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar("VSub", self.TRACKBAR_WINDOW, 0, 255, nothing)

    # Return the HSV min and max values of the control GUI 
    def get_hsv_filter_from_controls(self):
        hsv_filter = HsvFilter()
        hsv_filter.hMin = cv.getTrackbarPos('HMin', self.TRACKBAR_WINDOW)
        hsv_filter.sMin = cv.getTrackbarPos('SMin', self.TRACKBAR_WINDOW)
        hsv_filter.vMin = cv.getTrackbarPos('VMin', self.TRACKBAR_WINDOW)
        hsv_filter.hMax = cv.getTrackbarPos('HMax', self.TRACKBAR_WINDOW)
        hsv_filter.sMax = cv.getTrackbarPos('SMax', self.TRACKBAR_WINDOW)
        hsv_filter.vMax = cv.getTrackbarPos('VMax', self.TRACKBAR_WINDOW)
        hsv_filter.sAdd = cv.getTrackbarPos('SAdd', self.TRACKBAR_WINDOW)
        hsv_filter.sSub = cv.getTrackbarPos('SSub', self.TRACKBAR_WINDOW)
        hsv_filter.vAdd = cv.getTrackbarPos('VAdd', self.TRACKBAR_WINDOW)
        hsv_filter.vSub = cv.getTrackbarPos('VSub', self.TRACKBAR_WINDOW)
        return hsv_filter

    # Apply the filter on the image and return the image
    def apply_hsv_filter(self, original_image, hsv_filter=None):
        # Convert image to HSV
        hsv = cv.cvtColor(original_image, cv.COLOR_BGR2HSV)

        # Use the current GUI by default
        if not hsv_filter:
            hsv_filter = self.get_hsv_filter_from_controls()

        # Add or subtract saturation and value
        h, s, v = cv.split(hsv)
        s = self.shift_channel(s, hsv_filter.sAdd)
        s = self.shift_channel(s, -hsv_filter.sSub)
        v = self.shift_channel(v, hsv_filter.vAdd)
        v = self.shift_channel(v, -hsv_filter.vSub)
        hsv = cv.merge([h, s, v])

        # Set the minimum and maximum HSV values to display
        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])

        # Apply the thresholds
        mask = cv.inRange(hsv, lower, upper)
        result = cv.bitwise_and(hsv, hsv, mask=mask)

        # Convert back to BGR format
        img = cv.cvtColor(result, cv.COLOR_HSV2BGR)

        return img

    # Adjust HSV channels
    def shift_channel(self, c, amount):
        if amount > 0:
            lim = 255 - amount
            c[c >= lim] = 255
            c[c < lim] += amount
        else:
            amount = -amount
            lim = amount
            c[c <= lim] = 0
            c[c > lim] -= amount
        return c


