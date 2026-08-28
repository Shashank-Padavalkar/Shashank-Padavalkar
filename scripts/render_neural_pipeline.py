"""Render the animated neural-network pipeline used in the profile README."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
BASE_PATH = ASSETS / "profile-terminal.png"
GIF_PATH = ASSETS / "profile-terminal.gif"
PNG_PATH = ASSETS / "profile-terminal.png"

WIDTH, HEIGHT = 1200, 520
FRAME_COUNT = 40
FRAME_DURATION_MS = 90

FONT_REGULAR = Path(r"C:\Windows\Fonts\consola.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\consolab.ttf")

BG = "#0d1117"
BG_ALT = "#101722"
PANEL = "#161b22"
BORDER = "#30363d"
MUTED = "#484f58"
TEXT = "#c9d1d9"
WHITE = "#f0f6fc"
BLUE = "#58a6ff"
LIGHT_BLUE = "#a5d6ff"
GREEN = "#3fb950"
ORANGE = "#ffa657"


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


FONT_11 = font(11)
FONT_12 = font(12)
FONT_13 = font(13)
FONT_13_BOLD = font(13, bold=True)
FONT_14 = font(14)
FONT_15_BOLD = font(15, bold=True)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def smoothstep(value: float) -> float:
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def phase(progress: float, start: float, end: float) -> float:
    return smoothstep((progress - start) / (end - start))


def interpolate(start: tuple[float, float], end: tuple[float, float], amount: float) -> tuple[float, float]:
    return (
        start[0] + (end[0] - start[0]) * amount,
        start[1] + (end[1] - start[1]) * amount,
    )


def reset_left_pane(base: Image.Image) -> Image.Image:
    frame = base.convert("RGB").copy()

    pane = Image.new("RGB", (WIDTH, HEIGHT), BG)
    pane_draw = ImageDraw.Draw(pane)
    for y in range(55, 519):
        amount = (y - 55) / 464
        color = (
            int(13 + 3 * amount),
            int(17 + 6 * amount),
            int(23 + 10 * amount),
        )
        pane_draw.line((0, y, 455, y), fill=color)

    for x in range(12, 456, 24):
        pane_draw.line((x, 55, x, 518), fill="#141d28", width=1)
    for y in range(67, 519, 24):
        pane_draw.line((2, y, 455, y), fill="#141d28", width=1)

    card_mask = Image.new("L", (WIDTH, HEIGHT), 0)
    card_mask_draw = ImageDraw.Draw(card_mask)
    card_mask_draw.rounded_rectangle((2, 2, 1198, 518), radius=20, fill=255)

    pane_mask = Image.new("L", (WIDTH, HEIGHT), 0)
    pane_mask_draw = ImageDraw.Draw(pane_mask)
    pane_mask_draw.rectangle((2, 55, 455, 518), fill=255)
    pane_mask = ImageChops.multiply(card_mask, pane_mask)
    frame.paste(pane, (0, 0), pane_mask)

    draw = ImageDraw.Draw(frame)
    draw.line((455, 75, 455, 500), fill=BORDER, width=2)
    return frame


def draw_glow_dot(frame: Image.Image, position: tuple[float, float], color: str, radius: int = 4) -> None:
    x, y = position
    draw = ImageDraw.Draw(frame, "RGB")
    draw.ellipse((x - radius * 2, y - radius * 2, x + radius * 2, y + radius * 2), outline=MUTED, width=1)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=WHITE)


def draw_dotted_row(
    draw: ImageDraw.ImageDraw,
    y: int,
    key: str,
    value: str,
    *,
    value_color: str = LIGHT_BLUE,
) -> None:
    draw.text((22, y), key, font=FONT_12, fill=ORANGE)
    draw.text((112, y), "." * 10, font=FONT_12, fill=MUTED)
    draw.text((205, y), value, font=FONT_12, fill=value_color)


def draw_input_tensor(draw: ImageDraw.ImageDraw, scan: float) -> tuple[float, float]:
    origin_x, origin_y = 26, 145
    cell, gap = 9, 2
    pixels = (
        "..####..",
        ".#....#.",
        "#..##..#",
        "#.#..#.#",
        "#..##..#",
        ".#....#.",
        "..####..",
        "........",
    )
    scan_row = int(scan * len(pixels))

    for row, pattern in enumerate(pixels):
        for col, bit in enumerate(pattern):
            x = origin_x + col * (cell + gap)
            y = origin_y + row * (cell + gap)
            active = bit == "#"
            fill = "#1b2735" if not active else "#254b6d"
            outline = "#253343"
            if row == scan_row:
                fill = LIGHT_BLUE if active else "#1b3951"
                outline = BLUE
            draw.rectangle((x, y, x + cell, y + cell), fill=fill, outline=outline)

    return origin_x + 8 * (cell + gap), origin_y + 4 * (cell + gap)


def draw_feature_maps(draw: ImageDraw.ImageDraw, activation: float) -> tuple[float, float]:
    x, y = 137, 145
    for layer in range(3, -1, -1):
        offset = layer * 5
        shade = "#132232" if layer else "#172b3f"
        edge = BLUE if activation > 0.45 and layer == 0 else "#29435a"
        draw.rounded_rectangle((x + offset, y - offset, x + 58 + offset, y + 87 - offset), radius=4, fill=shade, outline=edge, width=1)

    front_x, front_y = x, y
    grid = 6
    size = 7
    gap = 2
    wave_col = int(activation * grid)
    for row in range(grid):
        for col in range(grid):
            px = front_x + 5 + col * (size + gap)
            py = front_y + 16 + row * (size + gap)
            energy = (row * 3 + col * 5) % 7
            lit = activation > 0.15 and col <= wave_col and energy < 4
            draw.rectangle(
                (px, py, px + size, py + size),
                fill=BLUE if lit else "#1c3448",
                outline="#27465f",
            )
    return x + 73, y + 43


def draw_embedding(draw: ImageDraw.ImageDraw, activation: float) -> tuple[float, float]:
    x = 271
    ys = [149, 166, 183, 200, 217, 234]
    for index, y in enumerate(ys):
        node_activation = phase(activation, index / 8, (index + 2) / 8)
        radius = 5
        fill = GREEN if node_activation > 0.55 else "#193226"
        outline = "#54d174" if node_activation > 0.25 else "#2d5a3b"
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill, outline=outline)
    return x + 7, sum(ys) / len(ys)


def draw_output(draw: ImageDraw.ImageDraw, activation: float) -> tuple[float, float]:
    x, y, width, height = 321, 143, 116, 98
    edge = GREEN if activation > 0.75 else "#29435a"
    draw.rounded_rectangle((x, y, x + width, y + height), radius=5, fill="#111c28", outline=edge)
    draw.text((x + 10, y + 9), "CLASSIFIER", font=FONT_11, fill=TEXT)

    person_value = 0.998 * activation
    other_value = max(0.002 * activation, 0.0)
    bars = (("person", person_value, GREEN), ("other", other_value, MUTED))
    for index, (label, value, color) in enumerate(bars):
        row_y = y + 35 + index * 27
        draw.text((x + 9, row_y), label, font=FONT_11, fill=LIGHT_BLUE)
        bar_x = x + 57
        draw.rectangle((bar_x, row_y + 3, bar_x + 43, row_y + 11), fill="#1b2735", outline="#26394b")
        draw.rectangle((bar_x + 1, row_y + 4, bar_x + 1 + int(41 * value), row_y + 10), fill=color)
        percentage = f"{value * 100:4.1f}" if activation > 0.05 else " -- "
        draw.text((bar_x, row_y + 13), percentage, font=FONT_11, fill=color)
    return x, y + height / 2


def draw_pipeline(frame: Image.Image, index: int) -> Image.Image:
    draw = ImageDraw.Draw(frame)
    progress = index / (FRAME_COUNT - 1)

    input_activation = phase(progress, 0.00, 0.23) * (1.0 - phase(progress, 0.94, 1.00))
    conv_activation = phase(progress, 0.18, 0.48) * (1.0 - phase(progress, 0.94, 1.00))
    embed_activation = phase(progress, 0.42, 0.72) * (1.0 - phase(progress, 0.96, 1.00))
    output_activation = phase(progress, 0.68, 0.88) * (1.0 - phase(progress, 0.94, 1.00))

    draw.text((20, 76), "$", font=FONT_14, fill=GREEN)
    draw.text((38, 76), "demo --pipeline vision_cnn", font=FONT_14, fill=TEXT)
    draw.text((371, 78), f"{index + 1:02d}/{FRAME_COUNT}", font=FONT_11, fill=MUTED)

    stage_y = 119
    draw.text((34, stage_y), "INPUT", font=FONT_11, fill=ORANGE)
    draw.text((145, stage_y), "CONV", font=FONT_11, fill=ORANGE)
    draw.text((247, stage_y), "EMBED", font=FONT_11, fill=ORANGE)
    draw.text((333, stage_y), "OUTPUT", font=FONT_11, fill=ORANGE)

    input_end = draw_input_tensor(draw, input_activation)
    conv_center = draw_feature_maps(draw, conv_activation)
    embed_center = draw_embedding(draw, embed_activation)
    output_center = draw_output(draw, output_activation)

    input_anchor = (input_end[0] - 4, input_end[1])
    conv_anchor_left = (137, conv_center[1])
    conv_anchor_right = (conv_center[0], conv_center[1])
    embed_anchor = (271, embed_center[1])
    output_anchor = (321, output_center[1])

    edges = (
        (input_anchor, conv_anchor_left),
        (conv_anchor_right, embed_anchor),
        ((278, 149), output_anchor),
        ((278, 183), output_anchor),
        ((278, 217), output_anchor),
        ((278, 234), output_anchor),
    )
    for start, end in edges:
        draw.line((*start, *end), fill="#243747", width=1)

    if 0.13 <= progress <= 0.42:
        amount = phase(progress, 0.13, 0.42)
        draw_glow_dot(frame, interpolate(input_anchor, conv_anchor_left, amount), BLUE)
    if 0.34 <= progress <= 0.67:
        amount = phase(progress, 0.34, 0.67)
        draw_glow_dot(frame, interpolate(conv_anchor_right, embed_anchor, amount), LIGHT_BLUE)
    if 0.57 <= progress <= 0.88:
        amount = phase(progress, 0.57, 0.88)
        for offset, node_y in enumerate((149, 183, 217)):
            local = clamp(amount - offset * 0.08)
            draw_glow_dot(frame, interpolate((278, node_y), output_anchor, local), GREEN, radius=3)

    draw.text((25, 254), "[1×3×224×224]", font=FONT_11, fill=MUTED)
    draw.text((145, 254), "64×56²", font=FONT_11, fill=MUTED)
    draw.text((250, 254), "512", font=FONT_11, fill=MUTED)

    draw.text((20, 287), "— Tensor trace", font=FONT_13, fill=TEXT)
    draw.line((130, 294, 437, 294), fill=BORDER)

    draw_dotted_row(draw, 311, "tensor.in", "[1, 3, 224, 224]")
    draw_dotted_row(draw, 340, "conv.out", "[1, 64, 56, 56]")
    draw_dotted_row(draw, 369, "embedding", "[1, 512]")
    prediction = "PERSON  99.8%" if output_activation > 0.9 else "pending..."
    draw_dotted_row(draw, 398, "prediction", prediction, value_color=GREEN if output_activation > 0.9 else MUTED)

    status = (
        "ENCODING"
        if progress < 0.24
        else "CONVOLVING"
        if progress < 0.52
        else "EMBEDDING"
        if progress < 0.74
        else "INFERENCE_OK"
        if progress < 0.94
        else "RESET"
    )
    draw.rounded_rectangle((20, 443, 437, 487), radius=5, fill="#111c28", outline="#26394b")
    draw.text((31, 453), "backend", font=FONT_11, fill=ORANGE)
    draw.text((94, 453), "PyTorch", font=FONT_11, fill=LIGHT_BLUE)
    draw.text((171, 453), "batch", font=FONT_11, fill=ORANGE)
    draw.text((235, 453), "1", font=FONT_11, fill=LIGHT_BLUE)
    draw.text((306, 453), "status", font=FONT_11, fill=ORANGE)
    draw.text((348, 453), status, font=FONT_11, fill=GREEN if status == "INFERENCE_OK" else LIGHT_BLUE)

    return frame


def render() -> None:
    if not BASE_PATH.exists():
        raise FileNotFoundError(f"Base profile card not found: {BASE_PATH}")

    base = Image.open(BASE_PATH).convert("RGB")
    if base.size != (WIDTH, HEIGHT):
        raise ValueError(f"Expected {WIDTH}x{HEIGHT}, got {base.size[0]}x{base.size[1]}")

    clean_base = reset_left_pane(base)
    frames = [draw_pipeline(clean_base.copy(), index) for index in range(FRAME_COUNT)]

    completed_frame = 35
    palette_source = frames[completed_frame].quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    gif_frames = [
        frame.quantize(palette=palette_source, dither=Image.Dither.NONE)
        for frame in frames
    ]
    gif_frames[0].save(
        GIF_PATH,
        save_all=True,
        append_images=gif_frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=True,
        disposal=1,
    )

    frames[completed_frame].save(PNG_PATH, format="PNG", optimize=True)
    print(f"Rendered {GIF_PATH} ({GIF_PATH.stat().st_size:,} bytes)")
    print(f"Rendered {PNG_PATH} ({PNG_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    render()
