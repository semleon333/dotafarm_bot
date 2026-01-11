from dataclasses import dataclass, field
from time import sleep, time

import cv2
import numpy as np
from loguru import logger
from pyautogui import pixel, press, screenshot

import var
from data import CardData, Point, SummonData, menu_data
from functions import click
from Inventory import HerocardData, InventoryManager, herocard_list, shop_db
from scanner import scanner_instance


@dataclass
class BattleManager:
    scanner = scanner_instance
    summon_data: list[SummonData] = field(default_factory=list[SummonData])
    _menu_data = menu_data
    inventory: InventoryManager = field(default_factory=InventoryManager)
    courier_inventory: InventoryManager = field(default_factory=InventoryManager)

    win_flag: bool = False
    defeat_flag: bool = False
    _cycle_start_time: float = time()
    _tick30s_timer: int = 0
    _tick2m_timer: int = 0
    _cycle_runtime: float = 0.0
    _gold: int = 0
    _wood: int = 0
    _kills: int = 0
    _branch_lvl: int = 1  # 1, 2, ..., 9
    _branch_lvl_plus: int = 0  # 0, +1, +2, +3, +4, +5, ->up
    _branch_cost: tuple[int, ...] = (
        53,
        200,
        875,
        1500,
        3000,
        5000,
        10000,
        20000,
        50000,
    )
    _midas_shop_positions: tuple[Point, ...] = (
        Point(1710, 360),
        Point(1765, 360),
        Point(1825, 360),
        Point(1885, 360),
    )
    _cards_shop_positions: tuple[Point, ...] = (
        Point(1710, 440),
        Point(1765, 440),
        Point(1825, 440),
        Point(1885, 440),
    )
    _minimap_start_positions: tuple[Point, ...] = (Point(86, 925),)
    #
    HOTKEY_00: str = "z"
    #
    _inventory_slots_click_positions: dict[tuple[int, int], Point] = field(
        default_factory=dict[tuple[int, int], Point]
    )
    main_cards: dict[tuple[int, int], CardData] = field(
        default_factory=dict[tuple[int, int], CardData]
    )
    main_cards_bottom: dict[tuple[int, int], CardData] = field(
        default_factory=dict[tuple[int, int], CardData]
    )
    courier_cards: dict[tuple[int, int], CardData] = field(
        default_factory=dict[tuple[int, int], CardData]
    )
    courier_cards_bottom: dict[tuple[int, int], CardData] = field(
        default_factory=dict[tuple[int, int], CardData]
    )
    all_main_cards: dict[tuple[int, int], CardData] = field(
        default_factory=dict[tuple[int, int], CardData]
    )
    _cards_buying_count: dict[int, int] = field(default_factory=dict[int, int])

    def __post_init__(self):
        self._cards_buying_count = {
            1: 1,
            2: 1,
            3: 1,
            4: 1,
        }
        self.summon_data = [
            SummonData("resource", Point(450, 860), (221, 181, 11)),
            SummonData("magic_bottle", Point(530, 860), (4, 233, 251), 6),
            SummonData("card", Point(610, 860), (169, 131, 210), 8),
            # stars = [1 , 2 , 2, 3, 3, 4, 4, 5]
            SummonData("advanced", Point(690, 860), (72, 48, 26)),
        ]
        self.main_cards = {
            (0, 1): CardData(),
            (0, 2): CardData(),
            (1, 0): CardData(),
            (1, 1): CardData(),
            (1, 2): CardData(),
        }
        self.main_cards_bottom = {
            (2, 0): CardData(),
            (2, 1): CardData(),
            (2, 2): CardData(),
        }
        self.courier_cards = {
            (0, 0): CardData(),
            (0, 1): CardData(),
            (0, 2): CardData(),
            (1, 0): CardData(),
            (1, 1): CardData(),
            (1, 2): CardData(),
        }
        self.courier_cards_bottom = {
            (2, 0): CardData(),
            (2, 1): CardData(),
            (2, 2): CardData(),
        }
        self._inventory_slots_click_positions = {
            (0, 0): Point(1160, 970),
            (0, 1): Point(1230, 970),
            (0, 2): Point(1300, 970),
            (1, 0): Point(1160, 1015),
            (1, 1): Point(1230, 1015),
            (1, 2): Point(1300, 1015),
            (2, 0): Point(1160, 1060),
            (2, 1): Point(1230, 1060),
            (2, 2): Point(1300, 1060),
        }

    def set_cycle_start_time(self) -> None:
        self._cycle_start_time = time()

    def _update_runtime(self) -> None:
        self._cycle_runtime = time() - self._cycle_start_time

    def _update_gold(self) -> None:
        self._gold = self.scanner.scan_area(self.scanner.gold)

    def _update_wood(self) -> None:
        self._wood = self.scanner.scan_area(self.scanner.wood)

    def _update_kills(self) -> None:
        self._kills = self.scanner.scan_area(self.scanner.kills)

    def _update_main_cards_stars(self) -> None:
        self.inventory = self.scanner.scan_stars(self.inventory)
        logger.debug(f"\n{self.inventory.to_matrix_string}")

    def _tick30s(self) -> None:
        if self._cycle_runtime > self._tick30s_timer + 30 and not self._check_death():
            self._tick30s_timer += 30
            click(Point(1360, 990))

    def _manage_midas(self) -> None:
        logger.debug(f"wood: {self._wood}")
        r, g, b = pixel(1458, 996)
        logger.debug(f"midas_rgb: {r} {g} {b}")
        shop_map = (
            (1, 3, self._midas_shop_positions[0]),
            (3, 5, self._midas_shop_positions[1]),
            (5, 10, self._midas_shop_positions[2]),
            (10, float("inf"), self._midas_shop_positions[3]),
        )
        if r == g == b:
            for min_wood, max_wood, position in shop_map:
                if min_wood <= self._wood < max_wood:
                    if not self._check_death():
                        click(position)
                        self._wood -= min_wood
                        logger.debug(f"bought midas for {min_wood} wood")
                        logger.debug(f"w={self._wood}")
                        break

    def _manage_branch(self) -> None:
        upgrade_menu_positions = (Point(960, 470), Point(960, 550), Point(960, 630))
        logger.debug(
            f"    branch: {self._branch_lvl}.{self._branch_lvl_plus}, gold: {self._gold}"
        )
        if self._branch_lvl < 9:
            while (
                self._branch_lvl_plus < 6
                and self._gold > self._branch_cost[self._branch_lvl - 1] * 4
                and not self._check_death()
            ):
                logger.debug(f"->{self._branch_lvl}.{self._branch_lvl_plus}")
                press(self.HOTKEY_00)
                self._branch_lvl_plus += 1
                self._gold -= self._branch_cost[self._branch_lvl - 1]
                sleep(1)
            if self._branch_lvl_plus > 5:
                sleep(1)
                self._branch_lvl += 1
                self._branch_lvl_plus = 0
                for pos in upgrade_menu_positions:
                    click(pos)
        elif self._gold > 70000 and not self._check_death():
            press(self.HOTKEY_00)
            self._branch_lvl_plus += 1
            self._gold -= self._branch_cost[self._branch_lvl - 1]
        logger.debug(
            f" --> branch: {self._branch_lvl}.{self._branch_lvl_plus}, gold: {self._gold}"
        )

    def _manage_summon_bar(self) -> None:
        for summon in self.summon_data:
            logger.debug(f"name = {summon.name}")
            if (
                pixel(*summon.click_position) == summon.check_pixel_color
                and not (summon.name == "advanced" and summon.summon_count >= 3)
                and not (summon.name == "resource" and self._cycle_runtime > 26 * 60)
            ):
                click(summon.click_position)
                summon.summon_count += 1
            logger.debug(f"count= {summon.summon_count}")

    def _manage_main_cards(self) -> None:
        def final_buying_cards(self: BattleManager):
            logger.debug(f"card_count_by_stars: {card_count_by_stars}")
            match card_count_by_stars[stars]:
                case 1:
                    if self._gold > (price1 + price2):
                        click(self._cards_shop_positions[stars - 1])
                        click(self._cards_shop_positions[stars - 1])
                        self._cards_buying_count[stars] += 2
                        self._gold -= price1 + price2
                case 2:
                    if self._gold > price1:
                        click(self._cards_shop_positions[stars - 1])
                        self._cards_buying_count[stars] += 1
                        self._gold -= price1
                case _:
                    pass

        # card price: 1* liner, 2-4* 0==1
        price_by_star = {1: 500, 2: 2000, 3: 8000, 4: 32000}

        # logger.debug(f"\n\t{cards[0,1].stars}\t{cards[0,2].stars}\n{cards[1,0].stars}\t{cards[1,1].stars}\t{cards[1,2].stars}\n{cards[2,0].stars}\t{cards[2,1].stars}\t{cards[2,2].stars}")
        card_count_by_stars = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for _, _, slot in self.inventory:
            if slot.item.name == "empty":
                card_count_by_stars[0] += 1
                continue
            if slot.item.name in herocard_list:
                match slot.star:
                    case 1:
                        card_count_by_stars[1] += 1
                    case 2:
                        card_count_by_stars[2] += 1
                    case 3:
                        card_count_by_stars[3] += 1
                    case 4:
                        card_count_by_stars[4] += 1
                    case 5:
                        card_count_by_stars[5] += 1
                    case _:
                        pass

        logger.debug(f"card_count_by_stars: {card_count_by_stars}")

        if self._cycle_runtime > 90:
            stars = 1
            price1 = self._cards_buying_count[stars] * price_by_star[stars]
            price2 = price1 + price_by_star[stars]
            if card_count_by_stars[0] > 2:
                final_buying_cards(self)

        if self._cycle_runtime > 6 * 60:  # 12
            stars = 2
            price1 = self._cards_buying_count[stars] * price_by_star[stars]
            price2 = price1 + price_by_star[stars]
            if card_count_by_stars[0] > 2:
                final_buying_cards(self)

        if self._cycle_runtime > 10 * 60:  # 20
            stars = 3
            price1 = self._cards_buying_count[stars] * price_by_star[stars]
            price2 = price1 + price_by_star[stars]
            if card_count_by_stars[0] > 2:
                final_buying_cards(self)

        if self._cycle_runtime > 20 * 60:  # 25
            stars = 4
            price1 = self._cards_buying_count[stars] * price_by_star[stars]
            price2 = price1 + price_by_star[stars]
            if card_count_by_stars[0] > 1:
                final_buying_cards(self)

    def _manage_shop(self):
        if self._cycle_runtime > self._tick2m_timer + 120:
            self._tick2m_timer += 120
        if (
            self._cycle_runtime < self._tick2m_timer + 20
            and self._cycle_runtime > self._tick2m_timer + 100
        ):
            return
        ss_items = self.scanner.scan_secret_shop_items()
        for ss_item in ss_items:
            for const_item in shop_db:
                if ss_item == const_item.name:
                    pass
                    # match ss_item:

    def _manage_inventory(self):
        items_list = self.scanner.scan_inventory_items()
        # logger.debug(items_list)
        for row, col, slot in self.inventory:
            flag = False
            for item in shop_db:
                if item.name == items_list[row * 3 + col]:
                    logger.debug(f"\n{slot}\n{item}\n")
                    slot.item = item
                    flag = True
                    break
            if not flag:
                # logger.debug(f"\n{slot}\n{items_list[row * 3 + col]}\n")
                slot.item = HerocardData(items_list[row * 3 + col])

        for row, col, slot in self.inventory:
            if not self._check_death():
                match slot.item.name:
                    case "The Devouring Pill next door":
                        self.inventory.slot_click(col, row, 2, 0.05, "SECONDARY")
                    case _:
                        pass

    def _check_defeat(self, current_lvl: str) -> None:
        if (
            pixel(1555, 202) == (141, 98, 198)  # endgame pixel (212,84,82)
            and str(max(self.scanner.spam_extract(self.scanner.defeat, 3)))
            == current_lvl
        ):
            self.defeat_flag = True

    def _check_death(self) -> bool:
        # check black/nonblack pixel in branch inventory slot
        if pixel(1169, 951) == (57, 63, 67):
            logger.debug("Dead")
            return True
        else:
            return False

    def _manage_first_battle_buttons(self) -> None:
        r, g, b = pixel(1900, 330)
        logger.debug(f"midas_button= {r, g, b}")
        if (r, g, b) == (255, 197, 0):
            logger.debug("Midas bar is closed")
            click(Point(1900, 330))  # button for open midas bar
            click(Point(1670, 970))  # off damage and gold sprites

    def _walking(self) -> None:  # добавить для других стартовых позиций
        if self._cycle_runtime % 40 < 20:
            click(Point(200, 460), button="SECONDARY")
        else:
            click(Point(1600, 530), button="SECONDARY")

    def run_main_loop(self, current_lvl: str) -> dict[str, int | bool]:
        letter_position = Point(880, 350)
        sleep(2)
        click(
            self._minimap_start_positions[0],
            clicks=2,
            interval=0.2,
            duration=0.5,
        )  # COOP
        self._manage_first_battle_buttons()
        click(self._inventory_slots_click_positions[0, 1])
        click(letter_position)
        click(
            self._inventory_slots_click_positions[1, 0],
            clicks=2,
            interval=0.05,
            button="SECONDARY",
        )  # get swap-card in courier
        while True:
            if var.EXIT_FLAG:
                return {
                    "abort_normally": True,
                    "defeat_flag": self.defeat_flag,
                    "win_flag": self.win_flag,
                }
            sleep(0.1)
            if not var.PAUSE_FLAG:
                self._check_defeat(current_lvl)
                if self.defeat_flag == True:
                    break
                self._update_runtime()
                logger.debug(f"---start_cycle--- runtime= {self._cycle_runtime:.2f}")
                if self._cycle_runtime > 1810:
                    self.win_flag = True
                    break

                self._walking()
                self._update_gold()
                self._update_wood()
                self._update_kills()
                logger.debug(f"g={self._gold} w={self._wood} k={self._kills}")
                self._tick30s()
                self._manage_midas()
                self._manage_branch()
                self._manage_summon_bar()
                # self._manage_shop()

                if not self._check_death():
                    timer = time() - self._cycle_start_time
                    self._manage_inventory()
                    for row, col, slot in self.inventory:
                        if slot.item.name == "letter" and not self._check_death():
                            self.inventory.slot_click(col, row)
                            click(letter_position)
                    self._update_main_cards_stars()
                    self._manage_main_cards()
                    logger.debug(
                        f"inventory managment time: {time() - self._cycle_start_time - timer}"
                    )

                # self._tick120s()
                # click(Point(1360, 870))
                # sleep(1)
                # self.scanner.scan_secret_shop_items()
                press("f", 3, 0.2)
                logger.debug("")
        logger.debug(f"defeat: {self.defeat_flag} win: {self.win_flag}")
        if not self.defeat_flag:
            # что бы точно не промахнуться по времени
            sleep(20)
            click(self._menu_data.endgame.tower_pos)
            # ~32с время 1 волны башни, ~43с в целом, таймер отсчитывается не сразу
            sleep(50)
            cv2.imwrite(
                f"./logs/endgame/{current_lvl}_{int(time())}_tower.png",
                cv2.cvtColor(np.array(screenshot()), cv2.COLOR_RGB2BGR),
            )
            # забрать награду, любое место на экране
            click(Point(250, 600), interval=1)

        cv2.imwrite(
            f"./logs/endgame/{current_lvl}_{int(time())}_end.png",
            cv2.cvtColor(np.array(screenshot()), cv2.COLOR_RGB2BGR),
        )
        return {
            "abort_normally": False,
            "defeat_flag": self.defeat_flag,
            "win_flag": self.win_flag,
        }
