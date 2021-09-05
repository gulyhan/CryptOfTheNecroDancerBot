from threading import Thread, Lock

from computer_vision.vision import Vision
from computer_vision.hsv_filter import HsvFilter

# Constants
STAIRS_HSV_FILTER = HsvFilter(3, 63, 41, 19, 159, 211, 0, 0, 0, 0)
WALL_HSV_FILTER = HsvFilter(0, 100, 0, 31, 210, 240, 0, 0, 0, 0)


class Detection:
    # Thread attributs
    stopped = True
    lock = None

    # Attributs
    screenshot = None
    character_rectangles = []
    downstairs_rectangles = []
    wall_rectangles = []

    # CV
    vision_downstairs = None
    vision_character = None
    vision_wall = None


    def __init__(self):
        self.lock = Lock()
        self.vision_downstairs = Vision("img/matchTemplate_needles/cotn_downstairs.png")
        self.vision_character = Vision("img/matchTemplate_needles/cotn_character.png")
        self.vision_wall = Vision("img/matchTemplate_needles/cotn_wall.png")
        #vision_wall.init_control_gui()


    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()


    def update(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()


    def stop(self):
        self.stopped = True
    

    def run(self):
        # TODO: while loop can be slowed down
        while not self.stopped:
            if not self.screenshot is None:
                # Pre-process the image (filter)
                processed_image_for_wall = self.vision_wall.apply_hsv_filter(self.screenshot, WALL_HSV_FILTER)

                # Objets detection
                ch_rectangles = self.vision_character.find(self.screenshot, 0.50)
                # print("Rectangle character:", ch_rectangles)
                ds_rectangles = self.vision_downstairs.find(self.screenshot, 0.50, max_results=1)
                # print("Rectangle downstairs: ", ds_rectangles)
                wa_rectangles = self.vision_wall.find(processed_image_for_wall, 0.40, max_results=100)

                # Lock the thread while updating the results
                self.lock.acquire()
                self.character_rectangles = ch_rectangles
                self.downstairs_rectangles = ds_rectangles
                self.wall_rectangles = wa_rectangles
                self.lock.release()
