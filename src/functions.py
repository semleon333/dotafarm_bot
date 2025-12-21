from time import sleep

from loguru import logger
from pyautogui import mouseDown, mouseUp, moveTo, pixel

from data import Point


def approx_equal_pixel(
    pixel1: tuple[int, int, int], pixel2: tuple[int, int, int], tolerance: int
) -> bool:
    for i in range(3):
        if abs(pixel1[i] - pixel2[i]) > tolerance:
            return False
    return True


def click(
    point: Point,
    clicks: int = 1,
    interval: float = 0.1,
    button: str = "primary",
    duration: float = 0.15,
) -> None:
    """0.1 > move > 0.1 > click..interval..click > 0.1"""
    print(point, clicks, interval, button, duration)
    sleep(0.1)
    moveTo(point.to_tuple, duration=duration)
    sleep(0.1)
    for i in range(clicks):
        mouseDown(button=button)
        sleep(0.1)
        mouseUp(button=button)
        if clicks > 1:
            sleep(interval)
    sleep(0.1)


def click_slow(*args, **kwargs) -> None:
    defaults = {"duration": 0.5}
    final_kwargs = kwargs.copy()
    for key, value in defaults.items():
        if key not in final_kwargs:
            final_kwargs[key] = value
    click(*args, **final_kwargs)


'''
def click(*args, **kwargs):
    """duration=0.5"""
    my_defaults = {"duration": 0.5}
    final_kwargs = kwargs.copy()
    for key, value in my_defaults.items():
        if key not in final_kwargs:
            final_kwargs[key] = value
    pyautogui_click(*args, **final_kwargs)
'''
