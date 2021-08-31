import numpy as np
from threading import Thread, Lock
# Screenshot
import win32gui, win32ui, win32con

class WindowCapture:
    # Thread attribut
    stopped = True
    lock = None
    screenshot = None

    # Monitor width and height
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    def __init__(self, window_name=None):
        self.lock = Lock()

        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception("Window not found {}".format(window_name))

        # Get the window size
        '''
        window_rect = win32gui.GetWindowRect(self.hwnd)
        w = window_rect[2] - window_rect[0]
        h = window_rect[3] - window_rect[1]
        '''
    
        w = 1920
        h = 1080

        # Crop the window border
        top_border_pixel_size = 18       # title bar
        bottom_border_pixel_size = 20    # tasks bar
        right_border_pixel_size = 0
        left_border_pixel_size = 0
        self.w = w - right_border_pixel_size - left_border_pixel_size
        self.h = h - top_border_pixel_size - bottom_border_pixel_size
        '''
        self.cropped_x = window_rect[0] + left_border_pixel_size
        self.cropped_y = window_rect[1] + top_border_pixel_size
        '''
        self.cropped_x = 0 + left_border_pixel_size
        self.cropped_y = 0 + top_border_pixel_size

        # Set the cropped coordinates offset
        # To translate screenshot images into actual screen positions
        '''
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y
        '''
        self.offset_x = 0 + self.cropped_x
        self.offset_y = 0 + self.cropped_y


    def get_screenshot(self):
        # Get the window image data
        # https://stackoverflow.com/questions/3586046/fastest-way-to-take-a-screenshot-with-python-on-windows/3586280#3586280
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h) , dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # Save the screenshot   
        # dataBitMap.SaveBitmapFile(cDC, "img/debug.png")
        # https://stackoverflow.com/questions/41785831/how-to-optimize-conversion-from-pycbitmap-to-opencv-image
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # Drop the alpha channel
        img = img[...,:3]

        # Make image C_CONTIGIOUS to avoid errors like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        img = np.ascontiguousarray(img)

        return img

    # Translate a pixel position on a screenshot image to a pixel position on the screen
    # @param : pos = (x, y)
    # Warning : if you move the window being captured after execution was started
    # this will return incorrect coordinates
    # because the window position is only calculated in __init__ constructor
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)


    # Returns (width, height) the resolution of the game screen
    def get_game_resolution(self):
        return (self.w, self.h)
    

    # THREAD METHODS
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True


    def run(self):
        # TODO: while loop can be slowed down
        while not self.stopped:
            screenshot = self.get_screenshot()
            # lock the thread while updating the result
            self.lock.acquire()
            self.screenshot = screenshot
            self.lock.release()
    

    # STATIC METHODS  
    @staticmethod
    def show_window_names():
        # https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    @staticmethod
    def get_window_names():
        # https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
        windows = []
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
                windows.append(win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)
        return windows


