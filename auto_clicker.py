import pyautogui
import random
import time
from human_mouse import human_mouse_move
from pynput import mouse


# x 416
# y 275


# Ask the user the whereabout it wants to be clicked
# Store the x/y in variables
# use human_mouse to move the mouse to the x/y + randomness
# pause for a random amount of time

print("Click anywhere on the screen...")

click_x, click_y = None, None

# todo: adjust the offset due to dual screens
def on_click(x, y, button, pressed):
  global click_x, click_y
  if pressed:
    click_x = round(x)
    click_y = round(y)
    print(f"Mouse clicked at ({click_x}, {click_y})")
    return False

with mouse.Listener(on_click=on_click) as listener:
  listener.join()

print(f"No starting to click at {click_x}, {click_y}")

while True:
  x_var = random.uniform(-5, 5)
  y_var = random.uniform(-5, 5)

  pyautogui.moveTo(click_x + x_var, click_x + y_var)
  pyautogui.click()
  c = random.uniform(4, 10)
  time.sleep(c)