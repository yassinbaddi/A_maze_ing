import time
from typing import Dict, Tuple
from themes import globals
from themes.colors import RESET
from utils.globals import PATTERN_MIN_W, PATTERN_MIN_H, CELL_W


_PATH_CELL: Dict[frozenset, str] = {

    frozenset({"N", "S"}):           " ┃ ",
    frozenset({"E", "W"}):           "━━━",
    frozenset({"N", "E"}):           " ┗━",
    frozenset({"N", "W"}):           "━┛ ",
    frozenset({"S", "E"}):           " ┏━",
    frozenset({"S", "W"}):           "━┓ ",
}

BORDER_TOP_LEFT = "╔"
BORDER_TOP_RIGHT = "╗"
BORDER_BOT_LEFT = "╚"
BORDER_BOT_RIGHT = "╝"
BORDER_H = "═"
BORDER_V = "║"
BORDER_TOP_JOIN = "╦"
BORDER_BOT_JOIN = "╩"
BORDER_LEFT_JOIN = "╠"
BORDER_RIGHT_JOIN = "╣"


WALL_H = "━"
WALL_V = "┃"


START_CHAR = "S"
END_CHAR = "E"
PATTERN_CHAR = "▓"


_JUNCTION: Dict[Tuple[bool, bool, bool, bool], str] = {
    (True,  True,  True,  True):  "╋",
    (True,  True,  False, True):  "┻",
    (False, True,  True,  True):  "┳",
    (True,  False, True,  True):  "┫",
    (True,  True,  True,  False): "┣",
    (False, True,  True,  False): "┏",
    (True,  True,  False, False): "┗",
    (False, False, True,  True):  "┓",
    (True,  False, False, True):  "┛",
    (False, True,  False, True):  "━",
    (True,  False, True,  False): "┃",
}


def build_42_pattern():
    return {
        (0, 0), (1, 0),
        (2, 0), (2, 1), (2, 2),
        (3, 2), (4, 2),
        (0, 4), (0, 5), (0, 6),
        (1, 6),
        (2, 4), (2, 5), (2, 6),
        (3, 4),
        (4, 4), (4, 5), (4, 6),
    }


def center_pattern(pattern, maze_width, maze_height):

    shift_x = (maze_width - 7) // 2
    shift_y = (maze_height - 5) // 2

    result = set()
    for row, col in pattern:
        x = col + shift_x
        y = row + shift_y
        result.add((x, y))

    return result


def get_direction(cell_a, cell_b):
    dx = cell_b.x - cell_a.x
    dy = cell_b.y - cell_a.y

    if dx == 1:
        return "E"
    if dx == -1:
        return "W"
    if dy == 1:
        return "S"
    if dy == -1:
        return "N"
    return ""


def get_path_character(index, solution, visible_steps):
    connections = set()

    if index > 0:
        direction = get_direction(solution[index], solution[index - 1])
        connections.add(direction)

    if index < visible_steps - 1:
        direction = get_direction(solution[index], solution[index + 1])
        connections.add(direction)

    return _PATH_CELL.get(frozenset(connections), "━━━")


def get_junction_character(north, east, south, west):
    return _JUNCTION.get((north, east, south, west), " ")


def are_path_neighbors(path_index, cell_a, cell_b):
    if cell_a not in path_index or cell_b not in path_index:
        return False
    one_step_apart = abs(path_index[cell_a] - path_index[cell_b]) == 1
    return one_step_apart


class MazeRenderer:
    def __init__(self, maze):
        self.maze = maze
        maze_is_big_enough = (
            maze.width >= PATTERN_MIN_W and maze.height >= PATTERN_MIN_H
            )
        if maze_is_big_enough:
            self.pattern_cells = (
                center_pattern(build_42_pattern(), maze.width, maze.height)
                )
        else:
            self.pattern_cells = set()

    def render(self, solution=None, step=None, show_42=True):

        theme = globals.get_current_theme()
        grid = self.maze.grid
        w = self.maze.width
        h = self.maze.height
        path = solution or []
        limit = step if step is not None else len(path)
        path_index = {path[i]: i for i in range(limit)} if path else {}
        pattern_cells = self.pattern_cells if show_42 else set()

        lines = [self.draw_top_border(grid, w, theme)]
        for y in range(h):
            lines.append(self.draw_cell_row(
                grid, y, w, theme, path_index, path, pattern_cells))

            if y < h - 1:
                lines.append(self.draw_separator_row(
                    grid, y, w, theme, path_index))
            else:
                lines.append(self.draw_bottom_border(grid, w, theme))

        print("\n".join(lines))

    def render_animated(self, solution, delay=0.05, show_42=True):
        from utils.helpers import clear

        for step in range(1, len(solution) + 1):
            clear()
            self.render(solution=solution, step=step, show_42=show_42)
            time.sleep(delay)

        globals._show_path = True

    def draw_top_border(self, grid, w, theme):
        wall = theme["wall"]
        segment = BORDER_H * CELL_W
        line = f"{wall}{BORDER_TOP_LEFT}{segment}"

        for x in range(w - 1):
            has_wall = grid[0][x].walls["right"]
            join = BORDER_TOP_JOIN if has_wall else BORDER_H
            line += join + segment

        return line + f"{BORDER_TOP_RIGHT}{RESET}"

    def draw_bottom_border(self, grid, w, theme):
        wall = theme["wall"]
        segment = BORDER_H * CELL_W
        line = f"{wall}{BORDER_BOT_LEFT}{segment}"

        for x in range(w - 1):
            has_wall = grid[-1][x].walls["right"]
            join = BORDER_BOT_JOIN if has_wall else BORDER_H
            line += join + segment

        return line + f"{BORDER_BOT_RIGHT}{RESET}"

    def draw_cell_row(
        self, grid, y, w, theme, path_index, solution, pattern_cells
    ):
        wall = theme["wall"]
        path = theme["path"]
        line = f"{wall}{BORDER_V}{RESET}"

        for x in range(w):
            cell = grid[y][x]
            line += self.draw_cell(
                cell, theme, path_index,
                len(path_index), solution, pattern_cells
                )

            if x < w - 1:
                next_cell = grid[y][x + 1]
                if cell.walls["right"]:
                    line += f"{wall}{WALL_V}{RESET}"
                elif are_path_neighbors(path_index, cell, next_cell):
                    line += f"{path}{WALL_H}{RESET}"
                else:
                    line += " "
            else:
                line += f"{wall}{BORDER_V}{RESET}"

        return line

    def draw_cell(
        self, cell, theme, path_index,
        total, solution, pattern_cells
    ):
        #it is a path cell ['S' , 'E', '--- | ...']
        if cell in path_index:
            index = path_index[cell]

            if index == 0:
                return f"{theme['start']}{START_CHAR:^{CELL_W}}{RESET}"

            if index == total - 1:
                return f"{theme['end']}{END_CHAR:^{CELL_W}}{RESET}"

            char = get_path_character(index, solution, total)
            return f"{theme['path']}{char}{RESET}"

        # it is pattern cell ['p']
        if (cell.x, cell.y) in pattern_cells:
            return f"{theme['pat']}{PATTERN_CHAR:^{CELL_W}}{RESET}"
        # it is a regular cell ['   ']
        return " " * CELL_W

    def draw_separator_row(self, grid, y, w, theme, path_index):
        wall = theme["wall"]
        path = theme["path"]
        segment = WALL_H * CELL_W

        left_cap = BORDER_LEFT_JOIN if grid[y][0].walls["bottom"] else BORDER_V
        line = f"{wall}{left_cap}{RESET}"

        for x in range(w):
            cell = grid[y][x]
            cell_below = grid[y + 1][x]

            if cell.walls["bottom"]:
                line += f"{wall}{segment}{RESET}"
            elif are_path_neighbors(path_index, cell, cell_below):
                line += f"{path} ┃ {RESET}"
            else:
                line += " " * CELL_W

            if x < w - 1:
                north = cell.walls["right"]
                east = grid[y][x + 1].walls["bottom"]
                south = grid[y + 1][x].walls["right"]
                west = cell.walls["bottom"]
                junction = get_junction_character(north, east, south, west)
                line += f"{wall}{junction}{RESET}"
            else:
                right_cap = (
                    BORDER_RIGHT_JOIN if cell.walls["bottom"] else BORDER_V
                    )
                line += f"{wall}{right_cap}{RESET}"

        return line
