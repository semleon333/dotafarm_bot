import hashlib
from dataclasses import dataclass
from pathlib import Path
from time import time

import cv2
import numpy as np
import pyautogui
from cv2.typing import MatLike
from loguru import logger
from PIL import Image
from pytesseract import image_to_string  # type: ignore

from data import Area, Point
from functions import approx_equal_pixel
from Inventory import InventoryManager


def compare_images_mse(img1: MatLike, img2: MatLike, tolerance: int = 400) -> bool:
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    mse = np.mean((img1.astype(float) - img2.astype(float)) ** 2)
    # print(f"MSE: {mse:.2f}")
    if mse < tolerance:
        return True
    else:
        return False


@dataclass
class Scanner:
    gold: Area = Area(1590, 1055, 60, 20)
    wood: Area = Area(1731, 1055, 60, 20)
    kills: Area = Area(1840, 1055, 60, 20)
    defeat: Area = Area(1520, 162, 70, 40)
    inventory_area_start_point: Point = Point(1135, 946)

    def scan_area(self, area: Area) -> int:
        image = cv2.cvtColor(
            np.array(pyautogui.screenshot(region=area.to_tuple)), cv2.COLOR_RGB2BGR
        )
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f"./dbg_img/{str(time())}_scan_area.png", image)
        text = image_to_string(image, config="--psm 13 digits")  # type: ignore
        number_str = "".join(filter(str.isdigit, text))  # type: ignore
        return int(number_str) if number_str else 0

    def spam_extract(self, area: Area, count: int) -> list[int]:
        numbers: list[int] = []
        for _ in range(count):
            numbers.append(self.scan_area(area))
        logger.debug(f"numbers= {numbers}")
        return numbers

    def scan_stars(
        self, inventory: InventoryManager = InventoryManager()
    ) -> InventoryManager:
        # 1143, 981 первая звезда слева сверху, между соседними картами x = 63, y = 45, между звёздами х = 11, x = 6
        pixel_colors = (241, 185, 34)  # pixel star color on card
        base_x, base_y = 1143, 981
        card_offset_x, card_offset_y = 63, 45
        for row, col, slot in inventory:
            slot.update_star(0)
            if row == 2:
                pixel_colors = (186, 142, 24)
            star_positions = (
                (
                    1,
                    base_x + card_offset_x * col + 11 * 2,
                    base_y + card_offset_y * row,
                ),
                (
                    2,
                    base_x + card_offset_x * col + 11 + 5,
                    base_y + card_offset_y * row,
                ),
                (
                    3,
                    base_x + card_offset_x * col + 11,
                    base_y + card_offset_y * row,
                ),
                (
                    4,
                    base_x + card_offset_x * col + 6,
                    base_y + card_offset_y * row,
                ),
                (
                    5,
                    base_x + card_offset_x * col,
                    base_y + card_offset_y * row,
                ),
            )
            for i, x, y in star_positions:
                pix = pyautogui.pixel(x, y)
                # logger.debug(f"{x} {y} {pix} {pixel_colors}")
                if approx_equal_pixel(pix, pixel_colors, 10):
                    # logger.debug(f"{x} {y} {pix} {pixel_colors}")
                    slot.update_star(i)
        return inventory

    def _cvt_screenshot(
        self, x: int, y: int, w: int, h: int, cvt: int = cv2.COLOR_RGB2BGR
    ) -> MatLike:
        return cv2.cvtColor(np.array(pyautogui.screenshot(region=(x, y, w, h))), cvt)

    def _get_slot_image(
        self,
        main_region: MatLike,
        slot_x: int,
        slot_y: int,
        slot_delta: tuple[int, int],
        w: int,
        h: int,
        region_shift: tuple[int, int] = (0, 0),
    ) -> MatLike:
        x = region_shift[0] + slot_delta[0] * slot_x
        y = region_shift[1] + slot_delta[1] * slot_y
        return main_region[y : y + h, x : x + w]

    def _recognition_image(self, new_image: MatLike, db_dir_path: Path) -> str:
        files = [file for file in db_dir_path.glob("*") if file.is_file()]
        new_image_hash = hashlib.md5(new_image.tobytes()).hexdigest()
        logger.debug(f"finding hash: {new_image_hash}")
        for file in files:
            img = cv2.cvtColor(np.array(Image.open(file)), cv2.COLOR_RGB2BGR)
            name = file.name.removesuffix(".png")
            if compare_images_mse(new_image, img):
                logger.debug(f"Found: {name}")
                return name
            if name == new_image_hash:
                # logger.debug("dublicate image")
                return "unknown"
        cv2.imwrite(f"{db_dir_path}_new/{new_image_hash}.png", new_image)
        return "new"

    def _scan_slots(
        self,
        main_region_xy: tuple[int, int],
        main_region_wh: tuple[int, int],
        col_start: int,
        col_stop: int,
        row_start: int,
        row_stop: int,
        slot_delta: tuple[int, int],
        region_shift: tuple[int, int],
        region_size: tuple[int, int],
        path: Path,
    ) -> list[str]:
        image_list: list[str] = []
        main_region = self._cvt_screenshot(
            main_region_xy[0],
            main_region_xy[1],
            main_region_wh[0],
            main_region_wh[1],
            cv2.COLOR_RGB2BGR,
        )
        for row in range(row_start, row_stop):
            for col in range(col_start, col_stop):
                image_list.append(
                    self._recognition_image(
                        self._get_slot_image(
                            main_region,
                            col,
                            row,
                            slot_delta,
                            region_size[0],
                            region_size[1],
                            region_shift,
                        ),
                        path,
                    )
                )
        return image_list

    def scan_secret_shop_items(self) -> list[str]:
        # *
        # белый     (221, 221, 221)
        # зелёный   (79, 255, 8)
        # синий     (35, 49, 255)
        # фиолетовый(230, 46, 255)
        # оранжевый (255, 167, 0)
        # 100 discount pixel(54, 30) (20, 204, 147)
        # discount pixel    (54, 30) (229, 176, 36)
        main_region_xy = (1008, 842)
        main_region_wh = (395, 80)
        slot_delta = (64, 0)
        region_shift = (0, 0)
        region_size = (38, 38)
        return self._scan_slots(
            main_region_xy,
            main_region_wh,
            0,
            5,
            0,
            1,
            slot_delta,
            region_shift,
            region_size,
            Path("./config/shop_db"),
        )

    def scan_inventory_items(self) -> list[str]:
        main_region_xy = (1135, 946)
        main_region_wh = (186, 132)
        slot_delta = (63, 45)
        region_shift = (20, 18)
        region_size = (30, 10)

        image_list_top = self._scan_slots(
            main_region_xy,
            main_region_wh,
            0,
            3,
            0,
            2,
            slot_delta,
            region_shift,
            region_size,
            Path("./config/inv_db_top"),
        )

        image_list_bottom = self._scan_slots(
            main_region_xy,
            main_region_wh,
            0,
            3,
            2,
            3,
            slot_delta,
            region_shift,
            region_size,
            Path("./config/inv_db_bottom"),
        )

        return image_list_top + image_list_bottom


scanner_instance = Scanner()
