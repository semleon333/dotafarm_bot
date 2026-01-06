from collections.abc import Generator
from dataclasses import dataclass, field
from typing import Any

from data import Point
from functions import click

# from loguru import logger


herocard_list = [
    "Antimage",
    "Tinker",
    "Sniper",
    "Alchemist",
    "Meepo",
    "Tiny",
    "Sven",
    #
    "CrystalMaiden",
    "Blackbird",
    "Slark",
    "Beast",
    "Bounty Hunter",
    "Necrophos",
    "OmniKnight",
    #
    "Mirana",
    "Blademaster",
    "Abaddon",
    "GuardianOfLight",
    "Clinkz",
    "Phoenix",
    "Venomancer",
    #
    "Centaur",
    "Dark Rider",
    "Clockwork",
    "Morphling",
    "Templar",
    "Vengeance",
    "Zeus",
    #
    "Doctor",
    "Lich",
    "Butcher",
    "Pugna",
    "Mortred",
    "Lancer",
    "Spectre",
    #
    "SF",
    "Leshrac",
    "Earthshaker",
    "Axe",
    "Captain",
    "Doombringer",
    "TideHunter",
    #
    "Helicopter",
    "Invoker",
    "Medusa",
    "Lina",
    "Bara",
    "Luna",
    "Brist",
    #
    "Razor",
    "Windrunner",
    "Ogre",
]


@dataclass(frozen=True)
class HerocardData:
    name: str = ""
    star: int = 0
    is_usable_by_star: dict[int, bool] = field(
        default_factory=lambda: {
            1: False,
            2: False,
            3: False,
            4: False,
            5: False,
        }
    )


herocard_db: list[HerocardData] = [
    HerocardData("Antimage", 1),
    HerocardData("Antimage", 2),
    HerocardData("Antimage", 3),
    HerocardData("Antimage", 4),
    HerocardData("Antimage", 5),
    HerocardData("Antimage", 6),
    HerocardData("Tinker", 1),
    HerocardData("Tinker", 2),
    HerocardData("Tinker", 3),
    HerocardData("Tinker", 4),
    HerocardData("Tinker", 5),
    HerocardData("Tinker", 6),
    HerocardData("Abaddon", 1),
    HerocardData("Abaddon", 2),
    HerocardData("Abaddon", 3),
]


@dataclass(frozen=True)
class ShopItemData:
    name: str = ""
    star: int = 0
    # base_price_type: tuple[bool, bool, bool] = (False, False, False)
    base_price: int = 0
    is_inventory_available: bool = False
    is_usable: bool = False
    is_disposable: bool = False


@dataclass
class InventorySlot:
    item: HerocardData | ShopItemData = field(default_factory=HerocardData)
    star: int = 0

    def set_item(self, name: str):
        for const_name in ("empty", "branch", "letter", "unknown", "new"):
            if name == const_name:
                self.item = HerocardData(name)
        if isinstance(self.item, ShopItemData):
            for item in shop_db:
                if name == item.name:
                    self.item = item
        else:
            pass

    def update_star(self, star: int = 0):
        if isinstance(self.item, ShopItemData):
            self.star = self.item.star
        else:
            self.star = star


@dataclass
class InventoryManager:
    slot00: InventorySlot = field(default_factory=InventorySlot)  # branch
    slot01: InventorySlot = field(default_factory=InventorySlot)
    slot02: InventorySlot = field(default_factory=InventorySlot)
    slot10: InventorySlot = field(default_factory=InventorySlot)
    slot11: InventorySlot = field(default_factory=InventorySlot)
    slot12: InventorySlot = field(default_factory=InventorySlot)
    slot20: InventorySlot = field(default_factory=InventorySlot)
    slot21: InventorySlot = field(default_factory=InventorySlot)
    slot22: InventorySlot = field(default_factory=InventorySlot)
    _position_00: tuple[int, int] = (1135, 946)

    def __iter__(self) -> Generator[tuple[int, int, InventorySlot], Any, None]:
        """row, col, InventorySlot"""
        for row in range(3):
            for col in range(3):
                slot_name = f"slot{row}{col}"
                yield row, col, getattr(self, slot_name)

    def slot_click(
        self,
        col: int,
        row: int,
        clicks: int = 1,
        interval: float = 0.1,
        button: str = "primary",
        duration: float = 0.15,
    ):
        slot_delta = (63, 45)
        region_shift = (20, 18)
        click(
            Point(
                self._position_00[0] + col * slot_delta[0] + region_shift[0],
                self._position_00[1] + row * slot_delta[1] + region_shift[1],
            ),
            clicks,
            interval,
            button,
            duration,
        )

    @property
    def to_matrix_string(self) -> str:
        attrs = [
            self.slot00,
            self.slot01,
            self.slot02,
            self.slot10,
            self.slot11,
            self.slot12,
            self.slot20,
            self.slot21,
            self.slot22,
        ]
        max_len = max(8, *(len(attr.item.name) for attr in attrs))
        formatted = [f"{a.star}* {a.item.name}".ljust(max_len + 3) for a in attrs]
        rows = [" ".join(formatted[i : i + 3]) for i in range(0, 9, 3)]
        return "\n".join(rows)


"""inv = Inventory()
inv.slot00.item = HerocardData("SF")
inv.slot01.item = HerocardData("SF")
inv.slot02.item = HerocardData("SF")
inv.slot10.item = HerocardData("CrystalMaiden")
inv.slot11.item = HerocardData("SF")
inv.slot12.item = HerocardData("SF")
inv.slot20.item = HerocardData("SF")
inv.slot21.item = HerocardData("SF")
inv.slot22.item = HerocardData("SF")
logger.debug(f"\n{inv.to_matrix_string}")"""

shop_db: tuple[ShopItemData, ...] = (
    # grow card
    ShopItemData(
        "Low-end Imprint Card",
        1,
        400,
        is_inventory_available=True,
    ),  #
    ShopItemData(
        "Mid-range Imprint Card",
        3,
        15000,
        is_inventory_available=True,
    ),  # g 15000
    ShopItemData(
        "High-end Imprint Card",
        4,
        is_inventory_available=True,
    ),  #
    ShopItemData(
        "Extreme Imprint",
        5,
        is_inventory_available=True,
    ),  #
    # give card
    ShopItemData("1-star Card Pack", 2, 800),  #
    ShopItemData("2-star Card Pack", 3, 3000),  #
    ShopItemData("3-star Card Pack", 4, 18000),  #
    ShopItemData("4-star Card Pack", 5),  #
    # weather
    ShopItemData(
        "Sunny Doll",
        3,
        is_inventory_available=True,
    ),  # w
    ShopItemData(
        "Rainy Doll",
        3,
        is_inventory_available=True,
    ),  # w 2
    ShopItemData(
        "Sandstorm Doll",
        2,
        is_inventory_available=True,
    ),  #
    ShopItemData(
        "Milk Snow Ice City",
        2,
        is_inventory_available=True,
    ),  #
    # timestop
    ShopItemData(
        "Void Specter",
        2,
        1,
        is_inventory_available=True,
    ),  # w
    # stats g
    ShopItemData("Attack Claw", 1, 680),  # BAD +3 6 12 24 48
    ShopItemData("Chainmail", 1, 800),
    ShopItemData("Strength Glove", 1, 680),  # stats +20 40 80 160 320
    ShopItemData("Agility Sandals", 1, 680),
    ShopItemData("Intellect Cloak", 1, 680),
    ShopItemData("Haste Glove", 2, 1575),
    #
    ShopItemData("Ultimate Orb", 4),  # g 50000 w6
    ShopItemData("Hawkeye Bow", 1),  # agi
    ShopItemData("Mystic Staff", 4),  # g 42000 w 5 int
    ShopItemData("Xymsit's Plunder", 4),  # g 42000 w 5 str
    ShopItemData("Heart of the Dragon", 1),  # g 100000 w 12 str
    ShopItemData("Butterfly", 5),  #  g 100000 w 12 agi
    ShopItemData("Guinsoo's Scimitar of Evil", 1),  # g 100000 w 12 int
    #
    ShopItemData(
        "2-star Card Duplicator",
        2,
        is_inventory_available=True,
    ),  # g 10000
    ShopItemData(
        "4-Star Card Duplicator",
        4,
        is_inventory_available=True,
    ),
    ShopItemData(
        "5-Star Card Duplicator",
        5,
        is_inventory_available=True,
    ),
    ShopItemData(
        "Tiny Pocket",
        1,
        is_inventory_available=True,
    ),  # 200s -> card
    ShopItemData(
        "Instability Converter",
        1,
        is_inventory_available=True,
    ),
    ShopItemData(
        "Star-Upgrading Card",
        1,
        is_inventory_available=True,
    ),
    #
    ShopItemData("2-star Woodpile", 2),  # k 200 1-3w
    ShopItemData("3-star Woodpile", 3),  #
    ShopItemData("4-star Woodpile", 4),  # k 400 3-6w
    ShopItemData("1-star Gold Coin Pile", 1),  # k 100 1000-3000g
    ShopItemData("2-star Gold Coin Pile", 2),  #
    ShopItemData("3-star Gold Coin Pile", 3),  # k 400 5000-20000g
    ShopItemData("4-star Gold Coin Pile", 4),  #
    ShopItemData("Exchange 1 Star Wood for Money", 1),  #
    ShopItemData("Exchange 2-star Wood for Money", 2, 3),  # w>g
    ShopItemData("Exchange 4-star Wood for Money", 1),  #
    #
    ShopItemData("Challenge Refresh Voucher", 1),
    ShopItemData("American Aggregation", 1),
    ShopItemData("Monster Attraction Support", 3),  # w 5 darkseers1
    ShopItemData("Jar of Little Souls", 1, 2000),  # g 2000 w1 50-150
    ShopItemData("Spirit Urn", 2, 6000),  # g>k 100-300 w2
    ShopItemData("Great Soul Jar", 3),  # g 15000 w3
    ShopItemData("Great Soul Jar", 4),  #  w 4 400-1200 kills
    ShopItemData("Invulnerable Grand Soul Jar", 5),  # g 50000
    #
    ShopItemData("Tao Dao Foundation Building", 1),
    ShopItemData("Overdraft Future", 1),  # dis Adv button, next Adv for all players
    ShopItemData("Wrong Evolution", 1),  # 3 Advanceds
    ShopItemData("Regardless of the cost", 1),  # obtain 3 items currently in BM
    ShopItemData("Pig Brain Overload", 3),  # many refreshes BM
    ShopItemData("Free", 3),  # w 3 free next purchase
    ShopItemData("Free VIP", 1),
    ShopItemData("The electricity meter doesn't work", 3),  # w 3
    ShopItemData("Reincarnation", 1),  # reset lvl
    ShopItemData("Likes to farm", 1),  # gold generation efficiency
    ShopItemData("God of Wealth Arrives", 1),  # drop res on map
    ShopItemData(
        "The Devouring Pill next door",
        5,
        is_inventory_available=True,
    ),  # w 10 devour card
    ShopItemData("Basic Skill 1", 1),  # g 999 stat book
    ShopItemData("Basic Skill No. 2", 2, 4999),
    ShopItemData("Basic Skill No.3", 3),
    ShopItemData("Basic Skill #4", 4),  # +100% exp
    ShopItemData("Ultimate Leap", 5),  # +full atr
    ShopItemData("Rob!", 1),  # rob BM
    ShopItemData("Bounty Hunter's Glory", 1),  # chance steal item
    ShopItemData("Buy early, enjoy early", 1),  # 19-CR wood
    ShopItemData("Late purchase to enjoy discount", 1),  # CR wood
    ShopItemData("If you don't buy, you'll have to wait for a gift.", 1),
    ShopItemData("Buy one, get one free", 3),  # w5 double next purchase
    ShopItemData("Wukong", 1),
    ShopItemData("Anything goes", 4),  # k 600
    ShopItemData("Eat Interest", 3),  # k
    ShopItemData("Meat Valley is coming", 1),
    ShopItemData("Survivor", 2),  # k 150
    ShopItemData("Marksman Master", 1),  # k 233 +10%FBD
    ShopItemData("Marksman Master II", 1),
    ShopItemData("Crystal Sword", 2, 300),  # k 300
    ShopItemData("Daedalus's Demise", 5),  # k 1688
    ShopItemData("Yasha", 1),  #
    ShopItemData("Haste Boots", 1),  # k 100 +10 ms
    ShopItemData("Haste Boots (Strength)", 3),  # k 300
    ShopItemData("Haste Boots (Agility)", 3),  # k 300
    ShopItemData("Haste Boots (Intelligence)", 3),  # k 300
    ShopItemData("Haste Boots (All-Rounder)", 1),
    ShopItemData("Fei Xie", 1),
    ShopItemData("Kohler's Escape Dagger", 1),  # blink
    ShopItemData("Nihility Gem", 1),  # +1 mp regen
    ShopItemData("Healing Ring", 1),  # + hp regen
    ShopItemData("Tough Ball", 1),
    ShopItemData("Mini Blackout", 1),
    ShopItemData("Little Darkness", 1, 100),  # k desol +3
    ShopItemData("Diminish", 4),  # k 600
    ShopItemData("Quenching", 1),
    ShopItemData("Fiendish Dragonlance", 1),  # k 75
    ShopItemData("Hurricane Halberd", 5),  # k 800
    ShopItemData("Great Sword", 1, 150),  # k 150 +100 AD
    ShopItemData("Broadsword", 1, 150),  # k 150 +20% CD
    ShopItemData("Round Shield", 1),  # k 150
    ShopItemData("Plate Armor", 3),  # k 500
    ShopItemData("Phase Boots", 3),  # k 500 +24% BAD
    ShopItemData(
        "Once upon a time, there was an iron tree trunk", 1, 25
    ),  # k 25 +5 attrs
    ShopItemData("Noble Ring", 1),  # k 100 +18attrs
    ShopItemData("Strength Belt", 2),  # k 204
    ShopItemData("Elven Boots", 2),  # k 204
    ShopItemData("Mage Robe", 2),  # k 204
    ShopItemData("Demon Blade", 4),  # k
    ShopItemData("Sage Artifact", 5),  # k 1288 +50%fin
    ShopItemData("Broken Necronomicon", 1),  # k 100 10%+1k
    ShopItemData("Necronomicon", 4),  # k 50%+1k
    ShopItemData("Energy Ball", 1),  # k 150 +20MP
    ShopItemData("Vigor Ball", 1),  # k 150 +10% maxHP
    ShopItemData("Madness Mask", 2, 400),  # k 400 +20BH -10armor
    ShopItemData("Holy Sword", 1),
    ShopItemData(
        "Trade-in Card",
        1,
        is_inventory_available=True,
    ),
    ShopItemData("Refresh Price Reset Coupon", 1),
    ShopItemData("Killing Potion", 1),
    ShopItemData("Pengci", 1),
    ShopItemData("Black Market Refresh Voucher", 1),  # give refreshes
    # ?dublicates
    # ShopItemData("Ultimate Orb", 1),
    # ShopItemData("Hawkeye Bow", 1),
    # ShopItemData("Mystic Staff", 1),
    # ShopItemData("Simeister's Plunder", 1),
    #
    ShopItemData(
        "6★ Card Synthesizer",
        1,
        is_inventory_available=True,
    ),
    ShopItemData("reincarnation·portable", 1),
    ShopItemData("Zun Du Jia Du·plus", 1),
)
