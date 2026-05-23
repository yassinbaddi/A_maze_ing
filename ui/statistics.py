from mazegen.generator import MazeGenerator
from config.config import MazeConfig
from themes.colors import RESET, BOLD, DIM
from themes import globals


def show_info(mg: MazeGenerator, data: MazeConfig) -> None:
    total = mg.width * mg.height
    seed = mg.seed if mg.seed is not None else "random"
    theme = globals.theme_manager.current_name
    entry = data.entry
    exit_ = data.exit
    sol_len = globals._solution_length

    w = 44
    m = 17

    print()
    print(f"  {BOLD}╔{'═' * w}╗{RESET}")
    print(f"  {BOLD}║{'Maze Statistics':^{w}}║{RESET}")
    print(f"  {BOLD}╠{'═' * w}╣{RESET}")
    print(f"  {BOLD}║{RESET} {'Dimensions':<{m}}"
          f"{f'{mg.width} x {mg.height}':<{w - 18}}{BOLD}║{RESET}")
    print(f"  {BOLD}║{RESET} {'Total cells':<{m}}"
          f"{str(total):<{w - 18}}{BOLD}║{RESET}")
    print(f"  {BOLD}║{RESET} {'Solution len':<{m}}"
          f"{f'{sol_len} steps':<{w - 18}}{BOLD}║{RESET}")
    print(f"  {BOLD}║{RESET} {'Entry':<{m}}"
          f"{str(entry):<{w - 18}}{BOLD}║{RESET}")
    print(f"  {BOLD}║{RESET} {'Exit':<{m}}"
          f"{str(exit_):<{w - 18}}{BOLD}║{RESET}")
    print(f"  {BOLD}║{RESET} {'Perfect':<{m}}"
          f"{str(mg.perfect):<{w - 18}}{BOLD}║{RESET}")
    print(f"  {BOLD}║{RESET} {'Seed':<{m}}"
          f"{str(seed):<{w - 18}}{BOLD}║{RESET}")
    print(f"  {BOLD}║{RESET} {'Theme':<{m}}"
          f"{theme:<{w - 18}}{BOLD}║{RESET}")
    print(f"  {BOLD}║{RESET} {'Output file':<{m}}"
          f"{data.output_file:<{w - 18}}{BOLD}║{RESET}")
    print(f"  {BOLD}╚{'═' * w}╝{RESET}")
    print()
    input(f"  {DIM}Press Enter to continue...{RESET}")
