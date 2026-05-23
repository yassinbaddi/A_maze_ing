from typing import Any, Dict
from themes import ThemeManager

theme_manager = ThemeManager()
_show_path: bool = False
_solution_length: int = 0


def get_current_theme() -> Dict[str, Any]:
    return theme_manager.as_dict()


def rotate_theme() -> Dict[str, Any]:
    theme_manager.rotate()
    return theme_manager.as_dict()


def set_custom_theme(
    wall: int, path: int, start: int, end: int, pat: int,
) -> None:
    theme_manager.set_custom(wall, path, start, end, pat)
