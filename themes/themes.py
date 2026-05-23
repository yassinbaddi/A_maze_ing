from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from themes.colors import RESET


@dataclass(frozen=True)
class Theme:
    name:  str
    wall:  str
    path:  str
    start: str
    end:   str
    pat:   str
    reset: str = RESET


BUILT_IN_THEMES: List[Theme] = [
    Theme(
        name="42",
        wall="\033[38;5;255m",
        path="\033[38;5;51m",
        start="\033[38;5;46m",
        end="\033[38;5;196m",
        pat="\033[38;5;27m",
    ),
    Theme(
        name="default",
        wall="\033[38;5;244m",
        path="\033[38;5;226m",
        start="\033[38;5;46m",
        end="\033[38;5;196m",
        pat="\033[38;5;220m",
    ),
    Theme(
        name="ocean",
        wall="\033[38;5;25m",
        path="\033[38;5;87m",
        start="\033[38;5;46m",
        end="\033[38;5;196m",
        pat="\033[38;5;45m",
    ),
    Theme(
        name="fire",
        wall="\033[38;5;236m",
        path="\033[38;5;202m",
        start="\033[38;5;226m",
        end="\033[38;5;196m",
        pat="\033[38;5;214m",
    ),
    Theme(
        name="neon",
        wall="\033[38;5;54m",
        path="\033[38;5;201m",
        start="\033[38;5;46m",
        end="\033[38;5;199m",
        pat="\033[38;5;213m",
    ),
    Theme(
        name="matrix",
        wall="\033[38;5;232m",
        path="\033[38;5;46m",
        start="\033[38;5;255m",
        end="\033[38;5;196m",
        pat="\033[38;5;34m",
    ),
    Theme(
        name="sunset",
        wall="\033[38;5;174m",
        path="\033[38;5;129m",
        start="\033[38;5;82m",
        end="\033[38;5;196m",
        pat="\033[38;5;135m",
    ),
    Theme(
        name="arctic",
        wall="\033[38;5;153m",
        path="\033[38;5;21m",
        start="\033[38;5;45m",
        end="\033[38;5;197m",
        pat="\033[38;5;159m",
    ),
    Theme(
        name="cyberpunk",
        wall="\033[38;5;238m",
        path="\033[38;5;199m",
        start="\033[38;5;51m",
        end="\033[38;5;196m",
        pat="\033[38;5;93m",
    ),
    Theme(
        name="forest",
        wall="\033[38;5;130m",
        path="\033[38;5;118m",
        start="\033[38;5;82m",
        end="\033[38;5;208m",
        pat="\033[38;5;64m",
    ),
    Theme(
        name="midnight",
        wall="\033[38;5;17m",
        path="\033[38;5;105m",
        start="\033[38;5;87m",
        end="\033[38;5;161m",
        pat="\033[38;5;57m",
    ),
    Theme(
        name="candy",
        wall="\033[38;5;255m",
        path="\033[38;5;198m",
        start="\033[38;5;123m",
        end="\033[38;5;205m",
        pat="\033[38;5;219m",
    ),
    Theme(
        name="monochrome",
        wall="\033[1;37m",
        path="\033[38;5;240m",
        start="\033[1;37m",
        end="\033[38;5;250m",
        pat="\033[38;5;244m",
    ),
]


class ThemeManager:

    def __init__(self) -> None:
        self._index = 0
        self._custom: Optional[Theme] = None

    @property
    def current(self) -> Theme:
        return self._custom if self._custom else BUILT_IN_THEMES[self._index]

    @property
    def current_name(self) -> str:
        return self.current.name

    @property
    def total_themes(self) -> int:
        return len(BUILT_IN_THEMES)

    def rotate(self) -> Theme:
        self._custom = None
        self._index = (self._index + 1) % len(BUILT_IN_THEMES)
        return self.current

    def set_by_name(self, name: str) -> bool:
        for i, t in enumerate(BUILT_IN_THEMES):
            if t.name == name.lower():
                self._index = i
                self._custom = None
                return True
        return False

    def set_custom(
        self, wall: int, path: int, start: int, end: int, pat: int,
    ) -> None:
        self._custom = Theme(
            name="custom",
            wall=f"\033[38;5;{wall}m",
            path=f"\033[38;5;{path}m",
            start=f"\033[38;5;{start}m",
            end=f"\033[38;5;{end}m",
            pat=f"\033[38;5;{pat}m",
        )

    def reset(self) -> None:
        self._custom = None
        self._index = 0

    def as_dict(self) -> Dict[str, Any]:
        t = self.current
        return {
            "name": t.name,
            "wall": t.wall,
            "path": t.path,
            "start": t.start,
            "end": t.end,
            "pat": t.pat,
            "reset": t.reset,
        }

    def list_names(self) -> List[str]:
        return [t.name for t in BUILT_IN_THEMES]
