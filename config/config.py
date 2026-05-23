import sys
from dataclasses import dataclass
from typing import Optional, Tuple
from utils.globals import SIZE_MIN, SIZE_MAX


class ParseError(Exception):
    pass


class ValidationError(Exception):
    pass


@dataclass
class MazeConfig:
    width:       int
    height:      int
    entry:       Tuple[int, int]
    exit:        Tuple[int, int]
    output_file: str
    perfect:     bool = True
    seed:        Optional[int] = None


class MazeConfigParser:
    REQUIRED = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
    OPTIONAL = {"SEED"}
    ALL = REQUIRED | OPTIONAL

    def __init__(self, filepath: str) -> None:
        self._path = filepath
        self._raw: dict = {}

    def parse(self) -> MazeConfig:
        self._read_file()
        self._check_required()
        cfg = self._build()
        self._validate(cfg)
        return cfg

    def _read_file(self) -> None:
        try:
            with open(self._path) as f:
                for no, raw in enumerate(f, 1):
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        raise ParseError(
                            f"Line {no}: expected 'KEY = VALUE', got: {line}"
                        )
                    key, _, val = line.partition("=")
                    key = key.strip().upper()
                    if key == "OUTPUT_FILE":
                        import os
                        if os.path.isdir(val.strip()):
                            raise ParseError(f"{val.strip()} is a directory")
                    if key in self.ALL:
                        self._raw[key] = val.strip()
        except FileNotFoundError:
            raise ParseError(f"Config file not found: {self._path}")
        except OSError as e:
            raise ParseError(f"Cannot read {self._path}: {e}")

    def _check_required(self) -> None:
        keys_dic = set(self._raw)
        missing = [key for key in self.REQUIRED if key not in keys_dic]
        if missing:
            raise ValidationError(
                f"Missing required key(s): {', '.join(missing)}"
                )

    def _build(self) -> MazeConfig:
        output = self._raw["OUTPUT_FILE"]
        if not output:
            raise ValidationError("OUTPUT_FILE must not be empty")

        seed_raw = self._raw.get("SEED", "").strip()
        seed = self._int("SEED") if seed_raw else None

        return MazeConfig(
            width=self._int("WIDTH"),
            height=self._int("HEIGHT"),
            entry=self._coord("ENTRY"),
            exit=self._coord("EXIT"),
            output_file=output,
            perfect=self._bool("PERFECT"),
            seed=seed,
        )

    def _validate(self, c: MazeConfig) -> None:
        lo, hi = SIZE_MIN, SIZE_MAX
        if not (lo <= c.width <= hi):
            raise ValidationError(f"WIDTH must be {lo}-{hi}, got {c.width}")
        if not (lo <= c.height <= hi):
            raise ValidationError(f"HEIGHT must be {lo}-{hi}, got {c.height}")
        ex, ey = c.entry
        qx, qy = c.exit
        if not (0 <= ex < c.width and 0 <= ey < c.height):
            raise ValidationError(f"ENTRY {c.entry} is outside the maze")
        if not (0 <= qx < c.width and 0 <= qy < c.height):
            raise ValidationError(f"EXIT {c.exit} is outside the maze")
        if c.entry == c.exit:
            raise ValidationError("ENTRY and EXIT must differ")

    def _int(self, key: str) -> int:
        try:
            return int(self._raw.get(key, ""))
        except ValueError:
            raise ValidationError(
                f"{key} must be an integer, got {self._raw.get(key)}"
            )

    def _coord(self, key: str) -> Tuple[int, int]:
        raw = self._raw[key]
        parts = raw.split(",")
        if len(parts) != 2:
            raise ValidationError(f"{key} must be 'x,y', got {raw}")
        try:
            return (int(parts[0].strip()), int(parts[1].strip()))
        except ValueError:
            raise ValidationError(
                f"{key} coordinates must be integers, got {raw}"
            )

    def _bool(self, key: str) -> bool:
        val = self._raw[key].lower()
        if val in {"true", "1"}:
            return True
        if val in {"false", "0"}:
            return False
        raise ValidationError(
            f"{key} must be 'true'/'false', got {self._raw[key]}"
        )


def get_data_config(config_file: str) -> MazeConfig:
    try:
        parser = MazeConfigParser(config_file)
        return parser.parse()
    except (ParseError, ValidationError) as err:
        print(f"\n  Error in config file: {err}\n")
        sys.exit(1)
