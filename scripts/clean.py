import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = [
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "build",
    "dist",
    "htmlcov",
]
FILE_PATTERNS = ["*.pyc", "*.pyo"]


def remove_directories() -> None:
    for relative_path in DIRECTORIES:
        target = ROOT / relative_path
        if target.exists():
            shutil.rmtree(target)


def remove_matching_files() -> None:
    for pattern in FILE_PATTERNS:
        for target in ROOT.rglob(pattern):
            if target.is_file():
                target.unlink()

    for target in ROOT.rglob("__pycache__"):
        if target.is_dir():
            shutil.rmtree(target)


def main() -> None:
    remove_directories()
    remove_matching_files()


if __name__ == "__main__":
    main()
