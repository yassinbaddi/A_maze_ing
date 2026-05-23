from utils.globals import PATTERN_MIN_W, PATTERN_MIN_H


def build_42_mask(width: int, height: int):
    if width < PATTERN_MIN_W or height < PATTERN_MIN_H:
        return None

    left = (width - 7) // 2
    top = (height - 5) // 2

    return {
        (left + 0, top + 0), (left + 0, top + 1), (left + 0, top + 2),
        (left + 1, top + 2), (left + 2, top + 2), (left + 2, top + 3),
        (left + 2, top + 4),

        (left + 4, top + 0), (left + 5, top + 0), (left + 6, top + 0),
        (left + 6, top + 1),
        (left + 4, top + 2), (left + 5, top + 2), (left + 6, top + 2),
        (left + 4, top + 3), (left + 4, top + 4), (left + 5, top + 4),
        (left + 6, top + 4),
    }
