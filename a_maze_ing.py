import os
import sys
from typing import List, Optional, Dict, Any

from mazegen.generator import MazeGenerator, Cell
from config.config import MazeConfig, get_data_config
from themes import globals
from themes.themes import BUILT_IN_THEMES
from themes.colors import (
    RESET, BOLD, DIM,
    CYAN, YELLOW, GREEN, RED,
)
from ui.drawing import MazeRenderer
from ui.statistics import show_info
from ui.menu import (
    read_int_advanced, read_int, msg, pause, fmt_coord,
    print_title, theme_preview, print_info_bar, print_menu,
)
from utils.helpers import clear
from utils.globals import SIZE_MAX, SIZE_MIN


class App:
    def __init__(self, config_file: str) -> None:
        self.config_file = config_file
        self._anim_delay_val = 0.05
        self.data: MazeConfig
        self.mg: MazeGenerator
        self.solution: List[Cell]
        self.renderer: MazeRenderer
        self._setup()

    # ── lifecycle ─────────────────────────────────────────────────

    def run(self) -> int:
        clear()
        print_title()
        self._full_redraw()
        self._loop()
        return 0

    def _setup(self) -> None:
        self.data = get_data_config(self.config_file)
        self.mg = self._make_maze(self.data)
        self.mg.generate(start=self.data.entry, mask=self._get_42_mask())
        self.solution = self.mg.get_solution(self.data.entry, self.data.exit)
        self.renderer = MazeRenderer(self.mg)
        globals._solution_length = len(self.solution)
        self._save_output()

    def _make_maze(self, d: MazeConfig) -> MazeGenerator:
        return MazeGenerator(
            width=d.width, height=d.height,
            seed=d.seed, perfect=d.perfect,
        )

    def _get_42_mask(self) -> Optional[set]:
        from utils.patterns import build_42_mask
        return build_42_mask(self.data.width, self.data.height)

    def _rebuild(self, new_generation: bool = True) -> None:
        if new_generation:
            self.mg = self._make_maze(self.data)
            self.mg.generate(start=self.data.entry, mask=self._get_42_mask())
        self.solution = self.mg.get_solution(self.data.entry, self.data.exit)
        self.renderer = MazeRenderer(self.mg)
        globals._show_path = False
        globals._solution_length = len(self.solution)
        self._save_output()

    def _save_output(self) -> None:
        try:
            with open(self.data.output_file, "w") as f:
                for y in range(self.mg.height):
                    row = "".join(
                        str(self.mg.grid[y][x].wall_code)[2].upper()
                        for x in range(self.mg.width)
                    )
                    f.write(row + "\n")
                f.write("\n")
                f.write(f"{self.data.entry[0]},{self.data.entry[1]}\n")
                f.write(f"{self.data.exit[0]},{self.data.exit[1]}\n")
                f.write(
                    self.mg.to_directions_string(self.solution) + "\n"
                )
        except PermissionError:
            msg(f"Cannot write to '{self.data.output_file}'", RED)
        except Exception as err:
            msg(f"Error saving: {err}", RED)

    def _full_redraw(self) -> None:
        clear()
        print_title()
        sol = self.solution if globals._show_path else None
        self.renderer.render(solution=sol, show_42=True)

    @property
    def _anim_delay(self) -> float:
        return self._anim_delay_val

    @_anim_delay.setter
    def _anim_delay(self, v: float) -> None:
        self._anim_delay_val = v

    # ── main loop ─────────────────────────────────────────────────

    def _loop(self) -> None:
        actions: Dict[int, Any] = {
            1: self._act_regenerate,
            2: self._act_toggle_path,
            3: self._act_themes_menu,
            4: self._act_animations,
            5: self._act_resize,
            6: self._act_set_entry_exit,
            7: self._act_toggle_perfect,
            8: self._act_statistics,
            9: self._act_export_menu,
        }
        while True:
            self._full_redraw()
            print_info_bar(self.mg, self.data)
            print_menu()
            sub = read_int_advanced("  ➤ ", 1, 9)
            if sub in actions:
                actions[sub]()

    # ══════════════════════════════════════════════════════════════
    #  1 — Regenerate
    # ══════════════════════════════════════════════════════════════

    def _act_regenerate(self) -> None:

        self._full_redraw()

        while True:
            print(
                f"\n  {BOLD}┌─── Regenerate "
                "────────────────────────────────┐"
                f"{RESET}"
            )
            print(f"  {BOLD}│{RESET}  {CYAN}1\t{RESET}  Regenerate a new maze"
                  f" {BOLD}                  │{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}2\t{RESET}  Set a specific seed "
                  f"and regenerate      {BOLD}│{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}3\t{RESET}  Back"
                  f"                                    {BOLD}│{RESET}")
            print(f"  {BOLD}│{RESET}  {RED}q\t{RESET}  Exit"
                  f"                                    {BOLD}│{RESET}")
            print(
                f"  {BOLD}└───────────────────────"
                f"────────────────────────┘{RESET}"
                )

            sub = read_int_advanced("  ➤ ", 1, 3)
            if sub == 1:
                if self.mg.seed:
                    msg(
                        "The maze has a seed. Nothing will be changed!", YELLOW
                    )
                    pause()
                else:
                    self._rebuild()
            elif sub == 2:
                raw = input(f"  {CYAN}Seed (integer):{RESET} ").strip()
                try:
                    self.data.seed = int(raw)
                    self._rebuild()
                except ValueError:
                    msg("Invalid integer — seed unchanged.", RED)
                    pause()
            elif sub == 3:
                break
            # self._full_redraw()

    # ══════════════════════════════════════════════════════════════
    #  2 — Toggle path
    # ══════════════════════════════════════════════════════════════

    def _act_toggle_path(self) -> None:
        globals._show_path = not globals._show_path
        self._full_redraw()

    # ══════════════════════════════════════════════════════════════
    #  3 — Themes & Colors
    # ══════════════════════════════════════════════════════════════

    def _act_themes_menu(self) -> None:
        while True:
            self._full_redraw()
            print(f"\n  {BOLD}┌─── Themes & Colors "
                  f"──────────────────────────────┐{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}1\t{RESET}  Cycle to next theme"
                  f"                      {BOLD}  │{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}2\t{RESET}  Pick theme by name"
                  f"                       {BOLD}  │{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}3\t{RESET}  Custom colors"
                  f" (256-color palette)         {BOLD} │{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}4\t{RESET}  Reset to default"
                  f" theme                   {BOLD}  │{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}5\t{RESET}  Back"
                  f"                                     {BOLD}  │{RESET}")
            print(f"  {BOLD}│{RESET}  {RED}q\t{RESET}  Exit"
                  f"                                       {BOLD}│{RESET}")
            print(f"  {BOLD}└──────────────────────────────"
                  f"────────────────────┘{RESET}")

            sub = read_int_advanced("  ➤ ", 1, 5)
            if sub == 1:
                globals.rotate_theme()
            elif sub == 2:
                self._act_pick_theme()
                break
            elif sub == 3:
                self._act_custom_colors()
                break
            elif sub == 4:
                globals.theme_manager.reset()
                msg("Theme reset to default ✓", GREEN)
                pause()
                self._full_redraw()
                break
            elif sub == 5:
                self._full_redraw()
                break

    def _act_pick_theme(self) -> None:
        names = globals.theme_manager.list_names()
        current = globals.theme_manager.current_name
        print(f"\n  {BOLD}Available themes:{RESET}\n")
        for i, n in enumerate(names, 1):
            bt = None
            for t in BUILT_IN_THEMES:
                if t.name == n:
                    bt = t
                    break
            preview = theme_preview(bt)
            marker = (
                f"  {GREEN}◂ current{RESET}" if n == current else ""
            )
            print(f"    {CYAN}{i:>2}{RESET}  {n:<14} {preview}{marker}")

        pick = read_int(f"\n  Choose (1-{len(names)}): ", 1, len(names))
        if pick is not None:
            globals.theme_manager.set_by_name(names[pick - 1])
            msg(
                f"Theme set to: {YELLOW}{names[pick - 1]}{RESET} ✓",
                GREEN,
            )
            pause()
        self._full_redraw()

    def _act_custom_colors(self) -> None:
        print(f"\n  {BOLD}256-Color Palette{RESET}\n")
        for i in range(256):
            print(f"\033[38;5;{i}m{i:>4}{RESET}", end="")
            if (i + 1) % 16 == 0:
                print()
        print(f"\n  {DIM}Enter a color code (0-255) for each element:{RESET}")

        colors = {}
        for label in ["Wall", "Path", "Start", "End", "42 Patt"]:
            val = None
            while val is None:
                val = read_int(f"  {CYAN}{label:<8}:{RESET} ", 0, 255)
            colors[label] = val

        globals.set_custom_theme(
            colors["Wall"], colors["Path"],
            colors["Start"], colors["End"],
            colors["42 Patt"]
        )
        msg("Custom colors applied ✓", GREEN)
        pause()
        self._full_redraw()

    # ══════════════════════════════════════════════════════════════
    #  4 — Animations
    # ══════════════════════════════════════════════════════════════

    def _act_animations(self) -> None:
        while True:
            self._full_redraw()
            delay_lbl = f"{self._anim_delay:.2f}s/step"
            box_width = 48
            title_left = f"─── Animation  [{delay_lbl}] "
            remaining = box_width - len(title_left)

            print(f"\n  {BOLD}┌{title_left}"
                  f"{'─' * remaining}┐{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}1\t{RESET}  Animate solution"
                  f" path reveal             {BOLD}│{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}2\t{RESET}  Adjust animation"
                  f" speed                   {BOLD}│{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}3\t{RESET}  Back"
                  f"                                     {BOLD}│{RESET}")
            print(f"  {BOLD}│{RESET}  {RED}q\t{RESET}  Exit"
                  f"                                     {BOLD}│{RESET}")
            print(f"  {BOLD}└{'─' * box_width}┘{RESET}")

            sub = read_int_advanced("  ➤ ", 1, 3)
            if sub == 1:
                self.renderer.render_animated(
                    self.solution,
                    delay=self._anim_delay,
                )
                self._full_redraw()
            elif sub == 2:
                self._act_set_speed()
            elif sub == 3:
                self._full_redraw()
                break

    def _act_set_speed(self) -> None:
        speeds = [
            ("1", "Fast      (0.02 s/step)", 0.02),
            ("2", "Normal    (0.05 s/step)", 0.05),
            ("3", "Slow      (0.12 s/step)", 0.12),
            ("4", "Very slow (0.25 s/step)", 0.19),
        ]
        print(f"\n  {BOLD}Animation speed:{RESET}")
        for num, label, val in speeds:
            marker = (
                f"  {GREEN}◂ current{RESET}"
                if self._anim_delay == val else ""
            )
            print(f"    {CYAN}{num}{RESET}  {label}{marker}")
        pick = read_int_advanced("  Choose (1-4): ", 1, 4)
        if pick is not None:
            self._anim_delay = speeds[pick - 1][2]
            msg(f"Speed → {speeds[pick - 1][1]} ✓", GREEN)
            pause()

    # ══════════════════════════════════════════════════════════════
    #  5 — Resize
    # ══════════════════════════════════════════════════════════════

    def _act_resize(self) -> None:
        print(
            f"\n  {BOLD}Current size:{RESET}"
            f" {self.mg.width} x {self.mg.height}"
            )
        print(
            f"  {DIM}(min {SIZE_MIN}x{SIZE_MIN},"
            f" max {SIZE_MAX}x{SIZE_MAX}){RESET}\n"
            )

        new_w = read_int(
            f"  {CYAN}New width  ({SIZE_MIN}-{SIZE_MAX}):{RESET} ",
            SIZE_MIN, SIZE_MAX
            )
        if new_w is None:
            self._full_redraw()
            return

        new_h = read_int(
            f"  {CYAN}New height ({SIZE_MIN}-{SIZE_MAX}):{RESET} ",
            SIZE_MIN, SIZE_MAX
            )
        if new_h is None:
            self._full_redraw()
            return

        self.data.width = new_w
        self.data.height = new_h
        self.data.entry = (0, 0)
        self.data.exit = (new_w - 1, new_h - 1)

        self._rebuild()
        self._full_redraw()

    # ══════════════════════════════════════════════════════════════
    #  6 — Set Entry / Exit
    # ══════════════════════════════════════════════════════════════

    def _act_set_entry_exit(self) -> None:
        while True:
            w, h = self.mg.width, self.mg.height
            entry_str = fmt_coord(self.data.entry)
            exit_str = fmt_coord(self.data.exit)
            clear()

            self._full_redraw()

            print(f"\n  {BOLD}┌─── Set Entry / Exit"
                  f" ────────────────────────────┐{RESET}")
            line1 = f"  Maze {w}x{h}  —  valid: x 0-{w - 1}, y 0-{h - 1}"
            print(f"  {BOLD}│{RESET}{line1:<49}{BOLD}│{RESET}")
            line2 = (f"  Current  Entry: {entry_str:<10}"
                     f"  Exit: {exit_str:<12}")
            print(f"  {BOLD}│{RESET}{line2:<49}{BOLD}│{RESET}")
            print(f"  {BOLD}│{RESET}{'':<49}{BOLD}│{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}1\t{RESET}  Change Entry"
                  f" point                      {BOLD}  │{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}2\t{RESET}  Change Exit "
                  f" point                      {BOLD}  │{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}3\t{RESET}  Swap Entry ↔"
                  f" Exit                       {BOLD}  │{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}4\t{RESET}  Reset to corners"
                  f" (0,0) → (w-1,h-1)     {BOLD}   │{RESET}")
            print(f"  {BOLD}│{RESET}  {CYAN}5\t{RESET}  Back"
                  f"                                    {BOLD}  │{RESET}")
            print(f"  {BOLD}│{RESET}  {RED}q\t{RESET}  Exit"
                  f"                                    {BOLD}  │{RESET}")
            print(f"  {BOLD}└{'─' * 49}┘{RESET}")

            sub = read_int_advanced("  ➤ ", 1, 5)

            if sub == 5:
                self._full_redraw()
                return

            if sub == 1:
                coord = self._read_coord("Entry", w, h, exclude=self.data.exit)
                if coord:
                    self.data.entry = coord
                    self._rebuild(new_generation=False)
                    msg(f"Entry → {fmt_coord(coord)} ✓", GREEN)
                    pause()
                break

            elif sub == 2:
                coord = self._read_coord("Exit", w, h, exclude=self.data.entry)
                if coord:
                    self.data.exit = coord
                    self._rebuild(new_generation=False)
                    msg(f"Exit → {fmt_coord(coord)} ✓", GREEN)
                    pause()
                    break

            elif sub == 3:
                tmp = self.data.entry
                self.data.entry = self.data.exit
                self.data.exit = tmp
                self._rebuild(new_generation=False)
                msg("Entry ↔ Exit swapped ✓", GREEN)
                pause()
                break

            elif sub == 4:
                self.data.entry = (0, 0)
                self.data.exit = (w - 1, h - 1)
                self._rebuild(new_generation=False)
                msg("Entry/Exit reset to corners ✓", GREEN)
                pause()
                break

    def _read_coord(
        self, label: str, w: int, h: int,
        exclude: Optional[tuple] = None,
    ) -> Optional[tuple]:
        from utils.patterns import build_42_mask
        try:
            x = read_int(
                f"  {CYAN}{label} X (0-{w - 1}):{RESET} ", 0, w - 1
            )
            y = read_int(
                f"  {CYAN}{label} Y (0-{h - 1}):{RESET} ", 0, h - 1
            )
            if exclude and (x, y) == exclude:
                msg("Entry and Exit cannot be the same cell.", RED)
                return None
            if self._get_42_mask():
                if (x, y) in build_42_mask(w, h):
                    msg("This is a pattern Cell", RED)
                    pause()
                    return None
            return (x, y)
        except (ValueError):
            msg("Invalid input.", RED)
            return None

    # ══════════════════════════════════════════════════════════════
    #  7 — Toggle perfect
    # ══════════════════════════════════════════════════════════════

    def _act_toggle_perfect(self) -> None:
        self.data.perfect = not self.data.perfect
        self._rebuild()
        self._full_redraw()

    # ══════════════════════════════════════════════════════════════
    #  8 — Statistics
    # ══════════════════════════════════════════════════════════════

    def _act_statistics(self) -> None:
        show_info(self.mg, self.data)

    # ══════════════════════════════════════════════════════════════
    #  9 — Export / Save
    # ══════════════════════════════════════════════════════════════

    def _act_export_menu(self) -> None:
        self._full_redraw()
        print(f"\n  {BOLD}┌─── Export & Save"
              f" ────────────────────────────────┐{RESET}")
        print(f"  {BOLD}│{RESET}  {CYAN}1\t{RESET}  Save config file"
              f" (current settings)     {BOLD}   │{RESET}")
        print(f"  {BOLD}│{RESET}  {CYAN}2\t{RESET}  Change output maze"
              f" file path             {BOLD}  │{RESET}")
        print(f"  {BOLD}│{RESET}  {CYAN}3\t{RESET}  Re-export maze to"
              f" current output file    {BOLD}  │{RESET}")
        print(f"  {BOLD}│{RESET}  {CYAN}4\t{RESET}  Back"
              f"                                     {BOLD}  │{RESET}")
        print(f"  {BOLD}│{RESET}  {RED}q\t{RESET}  Exit"
              f"                                       {BOLD}│{RESET}")
        print(f"  {BOLD}└──────────────────────────────"
              f"────────────────────┘{RESET}")

        sub = read_int_advanced("  ➤ ", 1, 4)
        if sub == 1:
            self._act_save_config()
        elif sub == 2:
            self._act_change_output_path()
        elif sub == 3:
            self._save_output()
            msg(f"Exported to '{self.data.output_file}' ✓", GREEN)
            pause()
            self._full_redraw()
        elif sub == 4:
            self._full_redraw()

    def _act_save_config(self) -> None:
        dest = input(
            f"  {CYAN}Save to{RESET}"
            f" (Enter = '{self.config_file}'): "
        ).strip() or self.config_file

        seed_val = self.mg.seed if self.mg.seed is not None else ''

        lines = [
            "# A-Maze-ing configuration file — auto-saved",
            f"WIDTH       = {self.data.width}",
            f"HEIGHT      = {self.data.height}",
            f"ENTRY       = {self.data.entry[0]},{self.data.entry[1]}",
            f"EXIT        = {self.data.exit[0]},{self.data.exit[1]}",
            f"OUTPUT_FILE = {self.data.output_file}",
            f"PERFECT     = {'true' if self.data.perfect else 'false'}",
            f"SEED        = {seed_val}",
        ]

        try:
            with open(dest, "w") as f:
                f.write("\n".join(lines) + "\n")
            msg(f"Config saved to '{dest}' ✓", GREEN)
        except Exception as err:
            msg(f"Save failed: {err}", RED)
        pause()

    def _act_change_output_path(self) -> None:
        print(f"\n  {BOLD}Current output file:{RESET}"
              f" {self.data.output_file}")
        raw = input(f"  {CYAN}New output file path:{RESET} ").strip()
        if not raw:
            msg("Path unchanged.", YELLOW)
        else:
            self.data.output_file = raw
            self._save_output()
            msg(f"Output path → '{raw}' ✓", GREEN)
        pause()


def main(args: list) -> int:
    if len(args) != 2:
        print(f"\n  Usage: python3 {args[0]} <config_file>\n")
        return 1
    path = args[1]
    if not os.path.exists(path):
        print(f"\n  Config file not found: {path}\n")
        return 1
    try:
        return App(path).run()
    except KeyboardInterrupt:
        print(f"\n  {YELLOW}Interrupted. Goodbye!{RESET}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
