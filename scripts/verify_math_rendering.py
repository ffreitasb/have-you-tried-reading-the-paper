"""Offline source-preservation and native Arithmatex rendering gate."""

from pathlib import Path

from math_rendering import check_corpus, check_rendering, formulas


def main():
    root = Path(__file__).resolve().parents[1]
    errors = check_corpus(root)
    count = 0
    for path in sorted((root / "docs").glob("*/*.md")):
        try:
            text = path.read_bytes().decode("utf-8")
            check_rendering(text)
            count += len(formulas(text))
        except ValueError as exc:
            errors.append(f"{path.relative_to(root).as_posix()}: {exc}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"PASS: {count} math expressions; preserved prose/TeX; native Arithmatex rendering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
