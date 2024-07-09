import pyautogui
from wind_mouse import wind_mouse

def human_mouse_move(start_x, start_y, dest_x, dest_y, **kwargs):
    """
    Moves the mouse from (start_x, start_y) to (dest_x, dest_y) using the WindMouse algorithm.
    Optionally takes a duration parameter for overriding the default WindMouse behavior.

    Args:
        start_x (int): Starting X coordinate.
        start_y (int): Starting Y coordinate.
        dest_x (int): Destination X coordinate.
        dest_y (int): Destination Y coordinate.
        **kwargs: Additional keyword arguments to pass directly to wind_mouse.
    """

    pyautogui.MINIMUM_DURATION = 0
    pyautogui.MINIMUM_SLEEP = 0

    def move_mouse_implementation(x, y):
        pyautogui.moveTo(x, y)

    wind_mouse(start_x, start_y, dest_x, dest_y, move_mouse=move_mouse_implementation, **kwargs)
