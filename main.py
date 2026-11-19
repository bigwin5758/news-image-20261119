"""Thursday 19 November 2026 — WORLD NEWS DAILY, landscape front page (v2).

The page leads with three heroes — Trump-Xi-Putin, GTA VI, Anthropic IPO —
followed by a 7-card grid of tiny briefs and a small world map strip along
the foot of the page. Landscape 1024x853.

DATE CHECK: this entry is pinned to the 19 Nov v2 artwork only. Nothing
here draws, edits, or re-encodes an image. The finished entry.png already
lives in this repo; this script only carries it into the output folder
after proving, byte for byte, that the file it carries is exactly that
artwork.

Every check below runs twice — once on the committed source, once on the
fresh copy — so a truncated, swapped, or corrupted file can never pass
silently.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

# --- pinned facts about the 19 Nov v2 artwork --------------------------------
EXPECTED_DIGEST = "c4c8702d60ee747591779ab4953f223eac7c3de147116db01d559a10075242f2"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 853
MAX_FILE_BYTES = 1048576
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SOURCE_FILENAME = "entry.png"


def _abort(message):
    """Print a failure to stderr and stop with a non-zero status."""
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def _digest_file(path):
    """Return the hex SHA-256 of the file at path, read in small chunks."""
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def _png_size(path):
    """Read width and height out of the PNG IHDR chunk.

    Layout of the first bytes of a PNG: 8-byte signature, then a 4-byte
    chunk length, the 4-byte ASCII tag "IHDR", then width (4 bytes) and
    height (4 bytes), both big-endian unsigned integers.
    """
    with open(path, "rb") as handle:
        head = handle.read(33)
    if len(head) < 24:
        _abort(f"{path.name}: file too short to hold a PNG header")
    if head[:8] != PNG_SIGNATURE:
        _abort(f"{path.name}: bad PNG magic bytes")
    if head[12:16] != b"IHDR":
        _abort(f"{path.name}: first chunk is not IHDR")
    width = int.from_bytes(head[16:20], byteorder="big")
    height = int.from_bytes(head[20:24], byteorder="big")
    return width, height


def _check_bytes(path, label):
    """Check size, signature, dimensions, and digest of one PNG file."""
    if not path.is_file():
        _abort(f"{label}: missing file {path}")
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        _abort(f"{label}: {path.name} is {size} bytes, over the {MAX_FILE_BYTES} limit")
    if size == 0:
        _abort(f"{label}: {path.name} is empty")
    width, height = _png_size(path)
    if width != EXPECTED_WIDTH or height != EXPECTED_HEIGHT:
        _abort(
            f"{label}: {path.name} is {width}x{height}, "
            f"expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}"
        )
    digest = _digest_file(path)
    if digest != EXPECTED_DIGEST:
        _abort(f"{label}: SHA-256 mismatch for {path.name}: got {digest}")
    print(f"{label}: {path.name} OK — {width}x{height}, {size} bytes, sha256 {digest[:12]}...")
    return size, digest


def _find_source():
    """Locate entry.png next to this script, wherever the repo was checked out."""
    here = Path(__file__).resolve().parent
    source = here / SOURCE_FILENAME
    if not source.exists():
        _abort(f"entry.png not found beside main.py in {here}")
    return source


def main():
    """Copy the verified 19 Nov v2 front page into the output folder."""
    source = _find_source()
    _check_bytes(source, "source")
    out_dir_text = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    out_dir = Path(out_dir_text)
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        _abort(f"cannot create output directory {out_dir}: {exc}")
    destination = out_dir / SOURCE_FILENAME
    try:
        shutil.copyfile(source, destination)
    except OSError as exc:
        _abort(f"copy to {destination} failed: {exc}")
    _check_bytes(destination, "output")
    print(f"done: wrote {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
