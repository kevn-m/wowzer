import mss
import numpy as np
import cv2 as cv
import time
import pyautogui
from multiprocessing import Process, Manager
import random
import pdb

from human_mouse import human_mouse_move

class ScreenCaptureAgent:
  def __init__(self, shared_data) -> None:
    self.img = None
    self.capture_process = None
    self.fps = None
    self.enable_cv_preview = True
    self.shared_data = shared_data

    self.target_images = {}  # Dictionary to store target images

    # Get the screen resolution
    self.w, self.h = pyautogui.size()
    print("Screen Resolution: " + "w: " + str(self.w) + " h:" + str(self.h))

    # Define the monitor region to capture
    self.monitor = {"top": 0, "left": 0, "width": self.w, "height": self.h}

  def load_targets(self, name, path):
    target_image = cv.imread(path, cv.IMREAD_COLOR)
    if target_image is None:
      print(f'Failed to load target image: {path}')
      return
    self.target_images[name] = target_image
    print(f"Loaded target image '{name} from '{path}'")

  def detect_image(self, image_name, threshold=0.5):
    if image_name not in self.target_images:
      print(f"Image '{image_name}' not loaded.")
      return None

    target_image = self.target_images[image_name]
    img_gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
    target_image_gray = cv.cvtColor(target_image, cv.COLOR_BGR2GRAY)

    result = cv.matchTemplate(img_gray, target_image_gray, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

    if max_val >= threshold:
      top_left = max_loc
      bottom_right = (top_left[0] + target_image.shape[1], top_left[1] + target_image.shape[0])
      self.shared_data['matched'] = (top_left, bottom_right)
      return (top_left, bottom_right)
    else:
      return None

  def move_mouse_to(self):
    matched = self.shared_data.get('matched', None)
    if matched is None:
      print(f"No image to move mouse to...")
    else:
      # Calculate the range for x and y coordinates within the bounding box
      x_range = (matched[0][0], matched[1][0])
      y_range = (matched[0][1], matched[1][1])

      # Shrink the range by a factor to move the clicks closer to the center
      shrink_factor = 0.3  # Adjust this factor to control how close to the center the clicks are
      x_shrink = int((x_range[1] - x_range[0]) * shrink_factor)
      y_shrink = int((y_range[1] - y_range[0]) * shrink_factor)

      # Adjusted range to avoid edges
      adjusted_x_range = (x_range[0] + x_shrink, x_range[1] - x_shrink)
      adjusted_y_range = (y_range[0] + y_shrink, y_range[1] - y_shrink)

      # Generate a random x and y coordinate within the adjusted bounding box
      random_x = random.randint(adjusted_x_range[0], adjusted_x_range[1])
      random_y = random.randint(adjusted_y_range[0], adjusted_y_range[1])

      print(f"Moving to {random_x}, {random_y}")
      pyautogui.moveTo(random_x, random_y)
      pyautogui.rightClick()

  def capture_screen(self):
    fps_report_time = time.time()
    fps_report_delay = 5
    n_frames = 1

    # Create a screen capture object
    with mss.mss() as sct:
      while True:
        # Capture the screen image
        self.img = sct.grab(self.monitor)
        self.img = np.array(self.img)

        for target_image_name in self.target_images:
          match = self.detect_image(target_image_name)
          if match:
            top_left, bottom_right = match
            cv.rectangle(self.img, top_left, bottom_right, (0, 255, 0), 2)
            cv.putText(self.img, target_image_name, (top_left[0], top_left[1] - 10),
                                   cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        if self.enable_cv_preview:
          # Resize the captured image
          small = cv.resize(self.img, (0, 0), fx=0.5, fy=0.5)

          if self.fps is None:
            fps_text = ""
          else: fps_text = f'FPS: {self.fps:.2f}'
          cv.putText(
            small,
            fps_text,
            (25, 50),
            cv.FONT_HERSHEY_DUPLEX,
            1,
            (255, 0, 255),
            1,
            cv.LINE_AA
          )

          # Display the resized image
          cv.imshow("Computer Vision", small)

        # Calculate and print the frames per second
        elapsed_time = time.time() - fps_report_time
        if elapsed_time >= fps_report_delay:
          self.fps = n_frames / elapsed_time
          # print("FPS: " + str(self.fps))
          n_frames = 0
          fps_report_time = time.time()
        n_frames += 1
        # Wait for a key press
        cv.waitKey(1)

class bcolors:
  PINK = '\033[95m'
  CYAN = '\033[96m'
  BLUE = '\033[94m'
  GREEN = '\033[92m'
  RED = '\033[91m'
  YELLOW = '\033[93m'
  ENDC = '\033[0m'


def print_menu():
  print(f'{bcolors.CYAN}Command Menu{bcolors.ENDC}')
  print(f'{bcolors.GREEN}\t r - run\t Start screen capture{bcolors.ENDC}')
  print(f'{bcolors.RED}\t s - stop\t Stop screen capture{bcolors.ENDC}')
  print(f'{bcolors.BLUE}\t m - move\t Move mouse{bcolors.ENDC}')
  print(f'\t q - quit\t Quit program')

if __name__ == "__main__":
  with Manager() as manager:
    shared_data = manager.dict()

    screen_agent = ScreenCaptureAgent(shared_data)
    screen_agent.load_targets("hat", "target_images/hat.png")

    while True:
      print_menu()
      user_input = input().strip().lower()

      if user_input == 'quit' or user_input == 'q':
        if screen_agent.capture_process is not None:
          print(f'{bcolors.PINK}Closed screen capture and terminated program{bcolors.ENDC}')
          screen_agent.capture_process.terminate()
        break

      elif user_input == 'run' or user_input == 'r':
        if screen_agent.capture_process is not None:
          print(f'{bcolors.YELLOW}Warning:{bcolors.ENDC} Capture process already running')
          continue
        screen_agent.capture_process = Process(
          target=screen_agent.capture_screen,
          args=(),
          name="screen capture process"
        )
        screen_agent.capture_process.start()
        print(f'{bcolors.GREEN}Screen capture started{bcolors.ENDC}')

      elif user_input == 'stop' or user_input == 's':
        if screen_agent.capture_process is None:
          print(f'{bcolors.YELLOW}Warning:{bcolors.ENDC} Capture is not running')
          continue
        screen_agent.capture_process.terminate()
        screen_agent.capture_process = None

      elif user_input == 'move' or user_input == 'm':
        screen_agent.move_mouse_to()

      else:
        print(f'{bcolors.RED}ERROR:{bcolors.ENDC} Invalid selection')

    print(f'{bcolors.RED}Exited{bcolors.ENDC}')