import argparse

from loguru import logger
from pynput import keyboard

import var
from MenuManager import menu_manager_instance


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--clearance",
        action="store_true",
        default=False,
        help="Прохождение башен начиная с --lvl до 10 раз, основываясь на clearance.json",
    )
    parser.add_argument(
        "--lvl",
        default="301",
        help="Башня и уровень (101-908)",
    )
    return parser.parse_args()


def on_press(key: keyboard.Key | keyboard.KeyCode | None) -> None:
    try:
        if key == keyboard.Key.esc:
            logger.debug("Exit")
            var.EXIT_FLAG = True
        if key == keyboard.Key.f6:
            logger.debug(f" {'Resume' if var.PAUSE_FLAG else 'Pause'}")
            var.PAUSE_FLAG = not var.PAUSE_FLAG
    except AttributeError:
        pass


listener = keyboard.Listener(on_press=on_press)
listener.start()

logger.add(
    "logs/debug.log",
    level="DEBUG",
    format="{time} {message}",
    rotation="1000 KB",
    # compression="zip",
)

if __name__ == "__main__":
    args = parse_args()
    logger.debug(f"Clearence: {args.clearance}, Level: {args.lvl}")
    resaults = menu_manager_instance.run_main_loop(
        one_lvl_spam=not args.clearance,
        current_lvl=args.lvl,
    )
    for res in resaults:
        logger.debug(f"{res}:{resaults[res]}")
