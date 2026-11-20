"""KiCad 8 Newstroke advances for the schematic overlap gate.

The advances are the glyph widths from the KiCad 8.0 Newstroke table:
width = (second_byte - first_byte) / 21, in units of the font size.
Line spacing follows STROKE_FONT::GetInterline: 1.68 * 0.9583 times the
glyph height. The first line box uses the 1.17 factor from FONT::getLinePositions.
"""

from __future__ import annotations

# ASCII 0x20..0x7E. Space is the first entry.
ADVANCES = (
    0.7619, 0.4762, 0.7619, 1.0000, 0.9524, 1.1429, 1.2381, 0.4762,
    0.6667, 0.6667, 0.7619, 1.2381, 0.4762, 1.2381, 0.4762, 1.0476,
    0.9524, 0.9524, 0.9524, 0.9524, 0.9524, 0.9524, 0.9524, 0.9524,
    0.9524, 0.9524, 0.4762, 0.4762, 1.2381, 1.2381, 1.2381, 0.8571,
    1.2857, 0.8571, 1.0000, 1.0000, 1.0000, 0.9048, 0.8571, 1.0000,
    1.0476, 0.4762, 0.7619, 1.0000, 0.8095, 1.1429, 1.0476, 1.0476,
    1.0000, 1.0476, 1.0000, 0.9524, 0.7619, 1.0476, 0.8571, 1.1429,
    0.9524, 0.8571, 0.9524, 0.6667, 0.6667, 0.6667, 0.5714, 0.7619,
    0.3810, 0.9048, 0.9048, 0.8571, 0.9048, 0.8571, 0.5714, 0.9048,
    0.9048, 0.4762, 0.4762, 0.8095, 0.5238, 1.3333, 0.9048, 0.9048,
    0.9048, 0.9048, 0.6190, 0.8095, 0.5714, 0.9048, 0.7619, 1.0476,
    0.8095, 0.7619, 0.8095, 0.6667, 0.9524, 0.6667, 0.7143,
)

SIZE = 1.27
INTERLINE = SIZE * 1.68 * 0.9583
LINE_H = SIZE * 1.17


def advance(char: str) -> float:
    code = ord(char)
    if 32 <= code <= 126:
        return ADVANCES[code - 32]
    return ADVANCES[ord("?") - 32]


def text_width(text: str, size: float = SIZE) -> float:
    return sum(advance(char) * size for char in text)


def line_boxes(x: float, y: float, text: str, justify: str, size: float = SIZE) -> list[tuple[float, float, float, float]]:
    """Axis-aligned boxes for a multiline label. Coordinates are millimetres, Y down.

    `justify` uses the KiCad tokens left, right, center, top and bottom.
    A missing horizontal token means center. A missing vertical token means center.
    """
    lines = text.split("\n") if text else []
    lines = [line for line in lines if line != ""]
    if not lines:
        return []
    horizontal = "center"
    vertical = "center"
    for token in justify.split():
        if token in {"left", "right", "center"}:
            horizontal = token
        elif token in {"top", "bottom"}:
            vertical = token
    widths = [text_width(line, size) for line in lines]
    count = len(lines)
    block = LINE_H + (count - 1) * (INTERLINE if size == SIZE else INTERLINE * size / SIZE)
    step = INTERLINE * (size / SIZE)
    line_h = LINE_H * (size / SIZE)
    if vertical == "top":
        top = y
    elif vertical == "bottom":
        top = y - block
    else:
        top = y - block / 2.0
    boxes = []
    for index, width in enumerate(widths):
        if horizontal == "left":
            left = x
        elif horizontal == "right":
            left = x - width
        else:
            left = x - width / 2.0
        this_top = top + index * step
        boxes.append((left, this_top, left + width, this_top + line_h))
    return boxes
