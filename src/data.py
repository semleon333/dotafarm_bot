from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def __len__(self) -> int:
        return 2

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    @property
    def to_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)


@dataclass(frozen=True)
class Area:
    x: int
    y: int
    w: int
    h: int

    def __len__(self) -> int:
        return 4

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.w
        yield self.h

    def __repr__(self) -> str:
        return f"(Area{self.x}, {self.y}, {self.w}, {self.h})"

    @property
    def to_tuple(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)


@dataclass
class CardData:
    name: str = ""
    stars: int = 0


@dataclass
class SummonData:
    name: str
    click_position: Point
    check_pixel_color: tuple[int, int, int]
    summon_count_limit: int = 0
    summon_count: int = 0


@dataclass
class MenuData:
    _towers: tuple[Point, ...] = (
        Point(330, 770),
        Point(620, 900),
        Point(1040, 760),
        Point(810, 510),
        Point(1160, 360),
        Point(950, 150),
        Point(650, 250),
        Point(1, 1),
        Point(1, 1),
    )
    _tower_lvls: tuple[Point, ...] = (
        Point(1490, 675),
        Point(1570, 675),
        Point(1650, 675),
        Point(1730, 675),
        Point(1490, 750),
        Point(1570, 750),
        Point(1650, 750),
        Point(1730, 750),
    )
    eggs: tuple[Point, Point, Point] = (
        Point(110, 730),
        Point(210, 730),
        Point(310, 730),
    )
    go_war: Point = Point(1700, 320)
    go: Point = Point(1600, 880)
    ready: Point = Point(960, 920)
    event_claim: Point = Point(1610, 310)

    class endgame:
        tower_pos: Point = Point(1660, 320)
        exit1_pos: Point = Point(960, 890)
        exit2_pos: Point = Point(1560, 900)

    class bottom_bar:
        position_feedbak: Point = Point(930, 1010)
        position_mall: Point = Point(1030, 1010)
        position_backpack: Point = Point(1130, 1010)
        position_battlepass: Point = Point(1230, 1010)
        position_event: Point = Point(1330, 1010)
        position_collection: Point = Point(1430, 1010)
        position_sacrifice: Point = Point(1530, 1010)
        position_dragon_remains: Point = Point(1630, 1010)
        position_gacha: Point = Point(1730, 1010)
        position_exchange_code: Point = Point(1830, 1010)

        class battlepass:
            claim_positions: tuple[Point, ...] = (
                Point(1700, 390),
                Point(1700, 485),
                Point(1700, 580),
                Point(1700, 675),
                Point(1700, 770),
            )

        class event:
            resident: Point = Point(220, 260)
            clearence: Point = Point(220, 260)
            remains: Point = Point(220, 260)
            week: Point = Point(220, 260)
            task: Point = Point(550, 170)
            event_gift_pack: Point = Point(750, 170)

    defeat: Area = Area(1520, 162, 70, 40)

    def get_tower_center(self, tower_id: int) -> Point:
        """id = 1, 2, ..., 9"""
        return self._towers[tower_id - 1]

    def get_tower_lvls_center(self, tower_lvl_id: int) -> Point:
        """id = 1, 2, ..., 8"""
        return self._tower_lvls[tower_lvl_id - 1]


menu_data = MenuData()
