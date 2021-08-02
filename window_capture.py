import numpy as np

# Screenshot
import win32gui, win32ui, win32con

class WindowCapture:
    # Monitor width and height
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    def __init__(self, window_name=None):
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception("Window not found {}".format(window_name))

        # Get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        # Crop the window border
        border_pixel = 10
        titlebar_pixels = 40
        self.w = self.w - (border_pixel * 2)
        self.h = self.h - titlebar_pixels - border_pixel
        self.cropped_x = border_pixel
        self.cropped_y = titlebar_pixels

        # Set the cropped coordinates offset
        # To translate screenshot images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y
    
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
        # dataBitMap.SaveBitmapFile(cDC, "debug.bmp")
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


    


