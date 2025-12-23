from dataclasses import dataclass
from time import time

import cv2
import numpy as np
import pytesseract  # type: ignore
from loguru import logger
from pyautogui import pixel, screenshot

from data import Area, CardData, Point
from functions import approx_equal_pixel
from tmp import SignaturePixels


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
        text = pytesseract.image_to_string(image, config="--psm 13 digits")  # type: ignore
        number_str = "".join(filter(str.isdigit, text))  # type: ignore
        return int(number_str) if number_str else 0

    def spam_extract(self, area: Area, count: int) -> list[int]:
        numbers: list[int] = []
        for _ in range(count):
            numbers.append(self.scan_area(area))
        logger.debug(f"numbers= {numbers}")
        return numbers

    def scan_stars(
        self, cards: dict[tuple[int, int], CardData], type: int
    ) -> dict[tuple[int, int], CardData]:
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

    def scan_secret_shop_items(self) -> list[SignaturePixels]:
        secret_shop_00_position = (1008, 842)
        secret_shop_pixel_list: list[SignaturePixels] = []
        for _ in range(5):
            pixel_list: list[tuple[int, int, int]] = []
            for i, j in [(0, 0), (0, 1), (1, 0), (1, 1)]:
                pixel_list.append(
                    pixel(
                        secret_shop_00_position[0] + i * 10,
                        secret_shop_00_position[1] + j * 10,
                    ),
                )
            secret_shop_pixel_list.append(SignaturePixels(*pixel_list))
        return secret_shop_pixel_list


scanner_instance = Scanner()
