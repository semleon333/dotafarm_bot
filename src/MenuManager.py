import json
from dataclasses import dataclass, field
from time import sleep

from loguru import logger

import var
from BattleManager import BattleManager
from data import menu_data
from functions import click


def load(path: str) -> dict[str, int]:
    with open(path, "r", encoding="utf-8") as f:
        s = json.load(f)
    return s


def save(json_dict: dict[str, int], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_dict, f, indent=4, ensure_ascii=False)


@dataclass
class MenuManager:
    _battle_manager = None
    _menu_data = menu_data
    _clearance: dict[str, int] = field(default_factory=dict[str, int])
    _wins_count: int = 0
    _defeats_count: int = 0
    war_results: dict[str, int | bool] = field(default_factory=dict[str, int | bool])

    def _get_lvl_by_clearance(self, start_lvl: str) -> str:
        current_lvl = start_lvl
        for lvl in self._clearance:
            if int(lvl) >= int(start_lvl) and self._clearance[lvl] < 10:
                logger.debug(f"{lvl}: {self._clearance[lvl]}")
                current_lvl = lvl
                self._clearance[lvl] += 1
                break
        return current_lvl

    def _click_eggs(self, count: tuple[int, int, int]) -> None:
        for i in range(3):
            click(self._menu_data.eggs[i], clicks=count[i], interval=0.2)

    def run_main_loop(
        self, one_lvl_spam: bool = False, current_lvl: str = "101"
    ) -> dict[str, int | bool]:
        logger.info("loaded")
        while True:
            if var.EXIT_FLAG:
                return self.war_results
            sleep(0.2)
            if not var.PAUSE_FLAG:
                self._battle_manager = BattleManager()

                if not one_lvl_spam:
                    self._clearance = load("config/clearance.json")
                    current_lvl = self._get_lvl_by_clearance(current_lvl)
                    # clearance +1
                click(self._menu_data.go_war)
                click(
                    self._menu_data.get_tower_center(int(current_lvl[0])),
                    duration=0.5,
                )
                click(
                    self._menu_data.get_tower_lvls_center(int(current_lvl[2])),
                    duration=0.5,
                )
                click(self._menu_data.go)
                self._click_eggs((10, 5, 2))

                click(self._menu_data.ready)
                sleep(5)
                self._battle_manager.set_cycle_start_time()
                self.war_results = self._battle_manager.run_main_loop(current_lvl)
                if self.war_results["win_flag"]:
                    self._wins_count += 1
                if self.war_results["defeat_flag"]:
                    self._defeats_count += 1
                self.war_results["wins_count"] = self._wins_count
                self.war_results["defeats_count"] = self._defeats_count
                if var.EXIT_FLAG:
                    return self.war_results
                if not one_lvl_spam:
                    save(self._clearance, "config/clearance.json")
                click(self._menu_data.endgame.exit1_pos)
                sleep(1)
                click(self._menu_data.endgame.exit2_pos)
                sleep(5)


menu_manager_instance = MenuManager()
