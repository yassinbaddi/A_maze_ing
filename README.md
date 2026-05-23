*This project has been created as part of the 42 curriculum by ybaddi, aelmanso.*

---

# A-Maze-ing 🌀🧩₪

## Description

**A-Maze-ing** is a terminal-based maze generator and solver written in Python. The program reads a configuration file to set up the maze parameters, generates a perfect or imperfect maze using a recursive backtracking algorithm, solves it automatically using BFS, and renders the result directly in the terminal with full Unicode box-drawing characters and a rich theming system.

Key features include:
- Procedural maze generation with optional seed for reproducibility
- Automatic BFS pathfinding between configurable entry and exit points
- Animated solution reveal with adjustable speed
- 13 built-in color themes + custom 256-color palette support
- The **"42" pattern** embedded as masked cells at the center of large mazes
- Interactive menu to resize, reconfigure, export, and manage the maze at runtime
- Output saved to a file in a structured format (wall codes + solution directions)

---

## Instructions

### Requirements

- Python 3.10+
- [`getch`](https://pypi.org/project/getch/) library

```bash
pip install getch
```

### Running the program

```bash
python3 a_maze_ing.py <config_file>
```

**Example:**

```bash
python3 a_maze_ing.py config.txt
```

### Config file format

The configuration file uses a simple `KEY = VALUE` format. Lines beginning with `#` are treated as comments and blank lines are ignored.

| Key           | Type        | Required | Description                                                  |
|---------------|-------------|----------|--------------------------------------------------------------|
| `WIDTH`       | integer     | ✅       | Width of the maze (3–100)                                    |
| `HEIGHT`      | integer     | ✅       | Height of the maze (3–100)                                   |
| `ENTRY`       | `x,y`       | ✅       | Entry cell coordinates (0-indexed)                           |
| `EXIT`        | `x,y`       | ✅       | Exit cell coordinates (0-indexed, must differ from ENTRY)    |
| `OUTPUT_FILE` | string      | ✅       | Path to the output file where the maze will be saved         |
| `PERFECT`     | true/false  | ✅       | Whether to generate a perfect maze (no loops)                |
| `SEED`        | integer     | ❌       | Optional RNG seed for reproducible generation                |

**Example config:**

```ini
# A-Maze-ing configuration
WIDTH       = 25
HEIGHT      = 20
ENTRY       = 0,0
EXIT        = 24,19
OUTPUT_FILE = output.txt
PERFECT     = true
SEED        = 42
```

### Output file format

The output file contains:
1. One row per maze line: hex wall codes (e.g. `F8A3...`)
2. A blank line
3. Entry coordinates: `x,y`
4. Exit coordinates: `x,y`
5. Solution as a direction string: `NESW...`

---

## Maze Generation Algorithm

### Recursive Backtracking (Iterative DFS)

The maze is generated using **Recursive Backtracking** (also known as the Depth-First Search or DFS algorithm with a stack).

**How it works:**
1. Start from the entry cell and mark it as visited.
2. Randomly choose an unvisited neighbor, remove the wall between them, and move there.
3. If no unvisited neighbors exist, backtrack using a stack until a cell with unvisited neighbors is found.
4. Repeat until all cells are visited.

**Why this algorithm?**

We chose Recursive Backtracking because:
- It produces **long, winding corridors** with a single guaranteed solution path — ideal for satisfying mazes.
- It is simple to implement and reason about.
- It supports **seeded generation** trivially, making mazes fully reproducible.
- It integrates cleanly with the **mask system** (the "42" pattern), since masked cells are pre-marked as visited and are skipped by the generator.

For **imperfect mazes**, additional walls are removed randomly after generation (`_rmv_more_walls`), introducing loops and multiple solution paths.

---

## Reusable Components

The following modules are designed to be reused in other projects:

### `mazegen/generator.py` — `MazeGenerator`
A self-contained maze generator class. It accepts width, height, seed, and a `perfect` flag. The `generate()` method accepts an optional `mask` (a set of `(x, y)` tuples) to exclude cells from the generation. It also exposes `get_solution()` (BFS pathfinder) and `to_directions_string()` independently.

```python
from mazegen.generator import MazeGenerator

mg = MazeGenerator(width=20, height=15, seed=42, perfect=True)
mg.generate(start=(0, 0))
solution = mg.get_solution((0, 0), (19, 14))
```

### `themes/` — `ThemeManager`
A theme management system with 13 built-in themes, rotation, named selection, and custom 256-color support. Can be dropped into any terminal project.

### `config/config.py` — `MazeConfigParser`
A standalone config file parser that validates types, ranges, and coordinates. Returns a typed `MazeConfig` dataclass. Reusable for any project requiring `.cfg`-style configuration.

### `ui/drawing.py` — `MazeRenderer`
Renders any `MazeGenerator` grid to the terminal using Unicode box-drawing characters, with optional solution overlay and animation.

---

## Team & Project Management


**How it evolved:**
- The 42-pattern mask required more care than anticipated — masked cells needed special handling both during generation and when validating entry/exit points.
- The theme system grew from a simple color dict to a full `ThemeManager` class to support rotation and custom colors cleanly.
- The animation system was added late but integrated well thanks to the existing `render()` method accepting a `step` parameter.

### What worked well

- The iterative DFS approach made seed-based reproducibility trivial.
- Separating the `MazeGenerator` from the `MazeRenderer` kept the logic clean and testable.
- The dataclass-based `MazeConfig` made passing configuration around the app safe and readable.

### What could be improved

- The menu system relies on raw terminal input (`getch`) which limits portability; a proper TUI library (e.g. `curses` or `textual`) would be more robust.
- The 42-pattern mask coordinates are duplicated between `ui/drawing.py` and `utils/patterns.py` — this should be unified.
- No unit tests exist; adding `pytest` coverage for the generator and parser would improve confidence in edge cases.

### Tools used

- **Python 3.10+** — primary language
- **getch** — raw keypress input for the interactive menu
- **Git** — version control and collaboration
- **VS Code** — editors
- **AI assistance (Arena)** — used to help draft the README, review docstrings, suggest refactoring for the `MazeRenderer` draw methods, and brainstorm edge cases for the config validator

---

## Resources
- [Struggling with DFS, Here’s the Ultimate Beginner’s Guide!](https://medium.com/@mahmoudayache2/struggling-with-dfs-and-bfs-heres-the-ultimate-beginner-s-guide-38d94bb9267b)
- [Maze Generation Algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive Backtracker — Jamis Buck's blog](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracker)
- [BFS Pathfinding — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Unicode Box Drawing Characters](https://www.compart.com/en/unicode/block/U+2500)
- [ANSI Escape Codes — 256-color support](https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit)
- [Python `dataclasses` documentation](https://docs.python.org/3/library/dataclasses.html)

### AI Usage

**Tool used:** Arena

AI was used for the following tasks:
- Suggesting cleaner class decomposition for the renderer (splitting `draw_cell_row` into smaller helpers)
- Reviewing edge cases in the config validator (empty `OUTPUT_FILE`, directory paths, coordinate bounds)

All algorithmic logic, rendering code, and architecture decisions were made by **Hara wa kan** team.