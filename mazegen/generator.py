import random
from collections import deque
from typing import List, Optional, Tuple
from mazegen.cell import Cell


try:
    from utils import globals
    MIN_SIZE = globals.SIZE_MIN
    MAX_SIZE = globals.SIZE_MAX
except ImportError:
    MIN_SIZE = 3
    MAX_SIZE = 100


class MazeGenerator:

    _MIN_SIZE = MIN_SIZE
    _MAX_SIZE = MAX_SIZE

    def __init__(
        self,
        width:   int = 20,
        height:  int = 15,
        seed:    Optional[int] = None,
        perfect: bool = True,
    ) -> None:
        if width < self._MIN_SIZE or height < self._MIN_SIZE:
            raise ValueError(
                f"Maze must be at least {self._MIN_SIZE}x{self._MIN_SIZE}, "
                f"got {width}x{height}"
            )
        if width > self._MAX_SIZE or height > self._MAX_SIZE:
            raise ValueError(
                f"Maze cannot exceed {self._MAX_SIZE}x{self._MAX_SIZE}, "
                f"got {width}x{height}"
            )
        self.width = width
        self.height = height
        self.seed = seed
        self.perfect = perfect
        self.grid: List[List[Cell]] = []
        self._generated: bool = False

        if seed is not None:
            random.seed(seed)

    def apply_mask(self, mask: set) -> None:
        if not mask:
            return
        for (x, y) in mask:
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue
            cell = self.grid[y][x]
            cell.walls = {
                "top": True, "bottom": True,
                "left": True, "right": True,
            }
            cell.wall_code = "0xf"
            cell.visited = True

            if y > 0:
                self.grid[y - 1][x].walls["bottom"] = True
            if y < self.height - 1:
                self.grid[y + 1][x].walls["top"] = True
            if x > 0:
                self.grid[y][x - 1].walls["right"] = True
            if x < self.width - 1:
                self.grid[y][x + 1].walls["left"] = True

    def _remove_walls(self, a: Cell, b: Cell) -> None:
        if a.x == b.x:
            if a.y > b.y:
                a.walls["top"] = False
                b.walls["bottom"] = False
            else:
                a.walls["bottom"] = False
                b.walls["top"] = False
        else:
            if a.x > b.x:
                a.walls["left"] = False
                b.walls["right"] = False
            else:
                a.walls["right"] = False
                b.walls["left"] = False

    def _unvisited_neighbors(self, cell: Cell) -> List[Cell]:
        x, y = cell.x, cell.y
        candidates = []
        if y > 0:
            candidates.append(self.grid[y - 1][x])
        if y < self.height - 1:
            candidates.append(self.grid[y + 1][x])
        if x > 0:
            candidates.append(self.grid[y][x - 1])
        if x < self.width - 1:
            candidates.append(self.grid[y][x + 1])
        return [n for n in candidates if not n.visited]

    def _calculate_hex(self) -> None:
        wall_bits = {"top": 1, "right": 2, "bottom": 4, "left": 8}
        for row in self.grid:
            for cell in row:
                total = sum(b for w, b in wall_bits.items() if cell.walls[w])
                cell.wall_code = hex(total)

    def _rmv_more_walls(self, chance: float = 0.18) -> None:
        if (self.width < 5 or self.height < 5
                or self.width == 9 and self.height == 7):
            chance = 0.4
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if x < self.width - 1:
                    nb = self.grid[y][x + 1]
                    if cell.walls["right"] and nb.walls["left"]:
                        if random.random() < chance:
                            cell.walls["right"] = False
                            nb.walls["left"] = False
                if y < self.height - 1:
                    nb = self.grid[y + 1][x]
                    if cell.walls["bottom"] and nb.walls["top"]:
                        if random.random() < chance:
                            cell.walls["bottom"] = False
                            nb.walls["top"] = False

    def generate(
        self,
        start: Tuple[int, int] = (0, 0),
        mask:  Optional[set] = None,
    ) -> "MazeGenerator":
        if (
            start[0] < 0 or start[0] >= self.width
            or start[1] < 0 or start[1] >= self.height
        ):
            raise ValueError(f"Start {start} is outside the maze bounds")

        self.grid = [
            [Cell(x, y) for x in range(self.width)]
            for y in range(self.height)
        ]
        self._generated = True

        if mask:
            for (x, y) in mask:
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y][x].visited = True

        stack: List[Cell] = []
        current = self.grid[start[1]][start[0]]
        current.visited = True

        while True:
            neighbors = self._unvisited_neighbors(current)
            if neighbors:
                chosen = random.choice(neighbors)
                stack.append(current)
                self._remove_walls(current, chosen)
                current = chosen
                current.visited = True
            elif stack:
                current = stack.pop()
            else:
                break

        if not self.perfect:
            self._rmv_more_walls()

        if mask:
            self.apply_mask(mask)

        self._calculate_hex()
        return self

    def get_solution(
        self, start: Tuple[int, int], end: Tuple[int, int],
    ) -> List[Cell]:
        if not self._generated:
            raise ValueError("Call generate() before get_solution()")
        for pos, label in [(start, "start"), (end, "end")]:
            if not (0 <= pos[0] < self.width and 0 <= pos[1] < self.height):
                raise ValueError(
                    f"The {label} position {pos} is outside the maze"
                )

        start_cell = self.grid[start[1]][start[0]]
        end_cell = self.grid[end[1]][end[0]]

        came_from: dict[Cell, Optional[Cell]] = {start_cell: None}
        queue = deque([start_cell])

        wall_to_dir = {
            "left":   (-1, 0), "right":  (1,  0),
            "top":    (0, -1), "bottom": (0,  1),
        }

        while queue:
            cell = queue.popleft()
            if cell is end_cell:
                break
            for wall, (dx, dy) in wall_to_dir.items():
                if cell.walls[wall]:
                    continue
                nx = cell.x + dx
                ny = cell.y + dy
                nb = self.grid[ny][nx]
                if nb not in came_from:
                    came_from[nb] = cell
                    queue.append(nb)

        path: List[Cell] = []
        node: Optional[Cell] = end_cell
        while node is not None:
            path.append(node)
            node = came_from.get(node)
        path.reverse()
        return path

    def to_directions_string(self, path: List[Cell]) -> str:
        MAP = {(0, -1): "N", (0, 1): "S", (1, 0): "E", (-1, 0): "W"}
        result = ""
        for i in range(len(path) - 1):
            dx = path[i + 1].x - path[i].x
            dy = path[i + 1].y - path[i].y
            result += MAP.get((dx, dy), "?")
        return result
