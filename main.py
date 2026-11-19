"""Copy the entry image to the output directory.

The program ships with its image (entry.png) and simply copies it to
$MAKEFUN_OUTPUT_DIR (or /output) as entry.png. Deterministic: the same
bytes come out on every run. Before copying it validates the source
five ways -- a valid PNG signature, the expected 1024x853 dimensions
read from the IHDR chunk, the expected SHA-256 digest, and a file size
within the competition's 1 MiB limit -- and after copying it re-checks
the output (size, SHA-256 digest, PNG signature, dimensions) so a
truncated, corrupted, or wrongly-sized write fails loudly instead of
shipping a broken image.

The image is the "WORLD NEWS DAILY" front page for Thursday
19 November 2026 (1024x853, landscape): "DATE CHECK" -- three hero
stories on top (Trump-Xi-Putin Shenzhen summit; GTA VI launch day;
Anthropic's $81.3bn IPO) plus a 7-card story grid, tiny briefs, and
a world map with numbered pins.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576  # competition limit: image must be at most 1 MiB
EXPECTED_DIMS = (1024, 853)  # width x height of entry.png
EXPECTED_SHA256 = (
    "c4c8702d60ee747591779ab4953f223eac7c3de147116db01d559a10075242f2"
)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    """Read (width, height) from a PNG file's IHDR chunk."""
    header = path.read_bytes()[:33]
    if len(header) < 33 or header[12:16] != b"IHDR":
        raise ValueError(f"{path} has no IHDR chunk")
    width = int.from_bytes(header[16:20], "big")
    height = int.from_bytes(header[20:24], "big")
    return width, height


def main() -> int:
    source = Path(__file__).resolve().parent / "entry.png"
    if not source.is_file():
        print(f"error: {source} not found", file=sys.stderr)
        return 1
    if source.read_bytes()[:8] != PNG_MAGIC:
        print(f"error: {source} is not a PNG file", file=sys.stderr)
        return 1
    try:
        width, height = png_dimensions(source)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if (width, height) != EXPECTED_DIMS:
        print(f"error: {source} is {width}x{height}, "
              f"expected {EXPECTED_DIMS[0]}x{EXPECTED_DIMS[1]}",
              file=sys.stderr)
        return 1
    if sha256_of(source) != EXPECTED_SHA256:
        print(f"error: {source} SHA-256 does not match the expected digest",
              file=sys.stderr)
        return 1
    if source.stat().st_size > MAX_BYTES:
        print(f"error: {source} is {source.stat().st_size} bytes, "
              f"over the {MAX_BYTES}-byte limit", file=sys.stderr)
        return 1
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"
    shutil.copyfile(source, dest)
    if dest.stat().st_size != source.stat().st_size:
        print("error: copied entry.png is not the same size as the source",
              file=sys.stderr)
        return 1
    if sha256_of(dest) != sha256_of(source):
        print("error: copied entry.png has a different SHA-256 than the source",
              file=sys.stderr)
        return 1
    if dest.read_bytes()[:8] != PNG_MAGIC:
        print("error: copied entry.png does not start with a PNG signature",
              file=sys.stderr)
        return 1
    try:
        out_width, out_height = png_dimensions(dest)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if (out_width, out_height) != EXPECTED_DIMS:
        print(f"error: copied entry.png is {out_width}x{out_height}, "
              f"expected {EXPECTED_DIMS[0]}x{EXPECTED_DIMS[1]}",
              file=sys.stderr)
        return 1
    print(f"wrote {dest} ({dest.stat().st_size} bytes, "
          f"sha256 {sha256_of(dest)[:16]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
