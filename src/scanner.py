from dataclasses import dataclass
from time import time

import cv2
import numpy as np
import pytesseract
from loguru import logger
from pyautogui import pixel, screenshot

from data import Area, Point
from functions import approx_equal_pixel


@dataclass
class Scanner:
    gold: Area = Area(1590, 1055, 60, 20)
    wood: Area = Area(1731, 1055, 60, 20)
    kills: Area = Area(1840, 1055, 60, 20)
    defeat: Area = Area(1520, 162, 70, 40)
    inventory_area_start_point: Point = Point(1135, 946)

    def scan_area(self, area: Area) -> int:
        image = cv2.cvtColor(
            np.array(screenshot(region=area.to_tuple)), cv2.COLOR_RGB2BGR
        )
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f"./dbg_img/{str(time())}_scan_area.png", image)
        text = pytesseract.image_to_string(image, config="--psm 13 digits")
        number_str = "".join(filter(str.isdigit, text))
        return int(number_str) if number_str else 0

    def spam_extract(self, area: Area, count: int) -> list[int]:
        numbers = []
        for i in range(count):
            numbers.append(self.scan_area(area))
        logger.debug(f"numbers= {numbers}")
        return numbers

    def scan_stars(self, cards: dict, type: int) -> dict:
        """type: 0: top, 1: bottom"""

        # 1143, 981 первая звезда слева сверху, между соседними картами x = 63, y = 45, между звёздами х = 11, x = 6
        pixel_colors = [(241, 185, 34), (186, 142, 24)]  # pixel star color on card
        BASE_X, BASE_Y = 1143, 981
        CARD_OFFSET_X, CARD_OFFSET_Y = 63, 45
        for card in cards:
            cards[card].stars = 0
            star_positions = (
                (
                    1,
                    BASE_X + CARD_OFFSET_X * card[1] + 11 * 2,
                    BASE_Y + CARD_OFFSET_Y * card[0],
                ),
                (
                    2,
                    BASE_X + CARD_OFFSET_X * card[1] + 11 + 5,
                    BASE_Y + CARD_OFFSET_Y * card[0],
                ),
                (
                    3,
                    BASE_X + CARD_OFFSET_X * card[1] + 11,
                    BASE_Y + CARD_OFFSET_Y * card[0],
                ),
                (
                    4,
                    BASE_X + CARD_OFFSET_X * card[1] + 6,
                    BASE_Y + CARD_OFFSET_Y * card[0],
                ),
                (5, BASE_X + CARD_OFFSET_X * card[1], BASE_Y + CARD_OFFSET_Y * card[0]),
            )
            for i, x, y in star_positions:
                if approx_equal_pixel(pixel(x, y), pixel_colors[type], 10):
                    cards[card].stars = i
        return cards

    # def scan_cards_names(self, cards: dict) -> dict:

    """def scan_secret_shop_items(self):
        secret_shop_00_position = (1008, 842)
        secret_shop_pixel_list = []
        for n in range(5):
            secret_shop_cell_pixel_list = []
            for i in (1, 2):
                for j in (1, 2):
                    secret_shop_cell_pixel_list.append(
                        pixel(
                            secret_shop_00_position[0] + 10 * i,
                            secret_shop_00_position[1] + 10 * j,
                        )
                    )
            secret_shop_pixel_list.append(secret_shop_cell_pixel_list)
        return secret_shop_pixel_list"""


scanner_instance = Scanner()
