

class Cell:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.visited: bool = False
        self.wall_code: str = "0xf"
        self.walls = {
            "top": True, "bottom": True,
            "left": True, "right": True,
        }
