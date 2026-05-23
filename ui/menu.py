from themes.colors import (
    RESET, BOLD, DIM,
    CYAN, YELLOW, GREEN, RED, MAGENTA, WHITE,
)
from themes import globals
import sys
import getch  # type: ignore[import-not-found]
from utils.helpers import clear


def read_int(prompt: str, lo: int, hi: int) -> int:
    while True:
        try:
            v = int(input(prompt))
            if lo <= v <= hi:
                return v
            else:
                print(f"  {RED}Enter a number between {lo} and {hi}.{RESET}")
        except ValueError as e:
            print(
                f"  {RED}Enter a number between {lo} and {hi}.\n  {e}.{RESET}"
                )


def read_int_advanced(prompt: str, lo: int, hi: int) -> int:
    while True:
        print(prompt, end='', flush=True)
        ch = getch.getch()

        if ch.lower() == 'q':
            clear()
            msg("\n  Goodbye! \n", GREEN)
            sys.exit(0)

        if ch.isdigit():
            v = int(ch)
            if lo <= v <= hi:
                print(ch)
                return v
            print(f"\n  Enter a number between {lo} and {hi}.")
        else:
            print(f"\n  Invalid key: {repr(ch)}")


def msg(text: str, color: str = WHITE) -> None:
    print(f"\n  {color}{text}{RESET}")


def pause() -> None:
    input(f"  {DIM}Press Enter to continue...{RESET}")


def fmt_coord(coord: tuple[int, int]) -> str:
    return f"({coord[0]}, {coord[1]})"


def print_title() -> None:
    print()
    print(f"  {BOLD}{CYAN} █████╗ \t███╗   ███╗ █████╗ ███████╗███████╗\t██╗"
          f"███╗   ██╗ ██████╗ {RESET}")
    print(f"  {BOLD}{CYAN}██╔══██╗\t████╗ ████║██╔══██╗╚══███╔╝██╔════╝\t██║"
          f"████╗  ██║██╔════╝ {RESET}")
    print(f"  {BOLD}{MAGENTA}███████║\t██╔████"
          f"╔██║███████║  ███╔╝ █████╗  \t██║"
          f"██╔██╗ ██║██║  ███╗{RESET}")
    print(f"  {BOLD}{MAGENTA}██╔══██║\t██║"
          f"╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝  \t██║"
          f"██║╚██╗██║██║   ██║{RESET}")
    print(f"  {BOLD}{CYAN}██║  ██║\t██║ ╚═╝ ██║"
          f"██║  ██║███████╗███████╗\t██║"
          f"██║ ╚████║╚██████╔╝{RESET}")
    print(f"  {BOLD}{CYAN}╚═╝  ╚═╝\t╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝\t╚═╝"
          f"╚═╝  ╚═══╝ ╚═════╝ {RESET}")


def theme_preview(t) -> str:
    return (
        f"{t.wall}▮{RESET}"
        f"{t.path}▮{RESET}"
        f"{t.start}▮{RESET}"
        f"{t.end}▮{RESET}"
        f"{t.pat}▮{RESET}"
    )


def print_info_bar(mg, data) -> None:
    t = globals.theme_manager.current
    name = globals.theme_manager.current_name
    perf = (
        f"{GREEN}perfect{RESET}" if mg.perfect else f"{YELLOW}imperfect{RESET}"
        )
    seed = str(mg.seed) if mg.seed is not None else "random"
    state = (
        f"{GREEN}visible{RESET}"
        if globals._show_path
        else f"{DIM}hidden{RESET}"
    )
    sol = globals._solution_length
    entry = fmt_coord(data.entry)
    exit_ = fmt_coord(data.exit)

    print(f"  {BOLD}{'─' * 68}{RESET}")

    print(
        f"  {BOLD}Size:{RESET} {mg.width}x{mg.height:<6}  "
        f"{BOLD}Theme:{RESET} {YELLOW}{name}{RESET} {theme_preview(t):<10}  "
        f"{BOLD}Seed:{RESET} {seed:<12}  "
        f"{BOLD}Path:{RESET} {sol} steps"
    )

    print(
        f"  {BOLD}Mode:{RESET} {perf:<10}  "
        f"{BOLD}Solution:{RESET} {state:<10}  "
        f"{BOLD}Entry:{RESET} {entry:<12}  "
        f"{BOLD}Exit:{RESET} {exit_:<10}  "
    )

    print(f"  {BOLD}{'─' * 68}{RESET}")


def print_menu() -> None:
    items = [
        ("1",  "Regenerate maze",            CYAN),
        ("2",  "Show / Hide solution path",  CYAN),
        ("3",  "Themes & Colors",            CYAN),
        ("4",  "Animation",                  CYAN),
        ("5",  "Resize maze",                CYAN),
        ("6",  "Set Entry / Exit points",    CYAN),
        ("7",  "Toggle perfect / imperfect", CYAN),
        ("8",  "Maze statistics",            CYAN),
        ("9",  "Export / Save config",       CYAN),
        ("q", "Exit",                       RED),
    ]
    print(f"  {BOLD}┌─── Main Menu {'─' * 47}┐{RESET}")
    for num, label, clr in items:
        print(
            f"  {BOLD}│{RESET}  {clr}{num:<3}{RESET}"
            f"  {label:<52}  {BOLD}│{RESET}"
        )
    print(f"  {BOLD}└{'─' * 61}┘{RESET}")
