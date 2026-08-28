"""Render the animated neural-network pipeline used in the profile README."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

WIDTH, HEIGHT = 1200, 520
FRAME_COUNT = 40
FRAME_DURATION_MS = 90

FONT_REGULAR = Path(r"C:\Windows\Fonts\consola.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\consolab.ttf")

THEMES = {
    "dark": {
        "page_bg": "#0d1117",
        "bg": "#0d1117",
        "bg_alt": "#101722",
        "panel": "#161b22",
        "border": "#30363d",
        "grid": "#141d28",
        "muted": "#8b949e",
        "faint": "#484f58",
        "text": "#c9d1d9",
        "white": "#f0f6fc",
        "blue": "#58a6ff",
        "light_blue": "#a5d6ff",
        "green": "#3fb950",
        "orange": "#ffa657",
        "surface": "#111c28",
        "surface_alt": "#1b2735",
        "cell_active": "#254b6d",
        "cell_edge": "#253343",
        "scan_off": "#1b3951",
        "feature_back": "#132232",
        "feature_front": "#172b3f",
        "feature_edge": "#29435a",
        "feature_cell": "#1c3448",
        "feature_cell_edge": "#27465f",
        "node_off": "#193226",
        "node_active_edge": "#54d174",
        "node_edge": "#2d5a3b",
        "trace": "#243747",
        "panel_edge": "#26394b",
    },
    "light": {
        "page_bg": "#ffffff",
        "bg": "#ffffff",
        "bg_alt": "#f6f8fa",
        "panel": "#f6f8fa",
        "border": "#d0d7de",
        "grid": "#eaeef2",
        "muted": "#57606a",
        "faint": "#8c959f",
        "text": "#24292f",
        "white": "#1f2328",
        "blue": "#0969da",
        "light_blue": "#0550ae",
        "green": "#1a7f37",
        "orange": "#bc4c00",
        "surface": "#f6f8fa",
        "surface_alt": "#eaeef2",
        "cell_active": "#b6d7f7",
        "cell_edge": "#d0d7de",
        "scan_off": "#ddf4ff",
        "feature_back": "#eef5fc",
        "feature_front": "#ddf4ff",
        "feature_edge": "#80b6e8",
        "feature_cell": "#dbeafe",
        "feature_cell_edge": "#a8cbed",
        "node_off": "#dafbe1",
        "node_active_edge": "#1a7f37",
        "node_edge": "#74c991",
        "trace": "#afb8c1",
        "panel_edge": "#d0d7de",
    },
}


def use_theme(name: str) -> None:
    palette = THEMES[name]
    global PAGE_BG, BG, BG_ALT, PANEL, BORDER, GRID
    global MUTED, FAINT, TEXT, WHITE, BLUE, LIGHT_BLUE, GREEN, ORANGE
    global SURFACE, SURFACE_ALT, CELL_ACTIVE, CELL_EDGE, SCAN_OFF
    global FEATURE_BACK, FEATURE_FRONT, FEATURE_EDGE, FEATURE_CELL, FEATURE_CELL_EDGE
    global NODE_OFF, NODE_ACTIVE_EDGE, NODE_EDGE, TRACE, PANEL_EDGE

    PAGE_BG = palette["page_bg"]
    BG = palette["bg"]
    BG_ALT = palette["bg_alt"]
    PANEL = palette["panel"]
    BORDER = palette["border"]
    GRID = palette["grid"]
    MUTED = palette["muted"]
    FAINT = palette["faint"]
    TEXT = palette["text"]
    WHITE = palette["white"]
    BLUE = palette["blue"]
    LIGHT_BLUE = palette["light_blue"]
    GREEN = palette["green"]
    ORANGE = palette["orange"]
    SURFACE = palette["surface"]
    SURFACE_ALT = palette["surface_alt"]
    CELL_ACTIVE = palette["cell_active"]
    CELL_EDGE = palette["cell_edge"]
    SCAN_OFF = palette["scan_off"]
    FEATURE_BACK = palette["feature_back"]
    FEATURE_FRONT = palette["feature_front"]
    FEATURE_EDGE = palette["feature_edge"]
    FEATURE_CELL = palette["feature_cell"]
    FEATURE_CELL_EDGE = palette["feature_cell_edge"]
    NODE_OFF = palette["node_off"]
    NODE_ACTIVE_EDGE = palette["node_active_edge"]
    NODE_EDGE = palette["node_edge"]
    TRACE = palette["trace"]
    PANEL_EDGE = palette["panel_edge"]


use_theme("dark")


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


FONT_11 = font(11)
FONT_12 = font(12)
FONT_13 = font(13)
FONT_13_BOLD = font(13, bold=True)
FONT_14 = font(14)
FONT_15_BOLD = font(15, bold=True)
FONT_16 = font(16)
FONT_17 = font(17)
FONT_25_BOLD = font(25, bold=True)


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


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def blend(start: str, end: str, amount: float) -> tuple[int, int, int]:
    start_rgb = hex_rgb(start)
    end_rgb = hex_rgb(end)
    return tuple(
        round(start_channel + (end_channel - start_channel) * amount)
        for start_channel, end_channel in zip(start_rgb, end_rgb)
    )


def draw_profile_row(draw: ImageDraw.ImageDraw, y: int, key: str, value: str) -> None:
    key_x = 495
    value_right = 1168
    leader_gap = 14

    key_width = draw.textlength(key, font=FONT_15_BOLD)
    value_width = draw.textlength(value, font=FONT_15_BOLD)
    value_x = value_right - value_width
    leader_x = key_x + key_width + leader_gap
    leader_right = value_x - leader_gap
    dot_width = draw.textlength(".", font=FONT_15_BOLD)
    dot_count = max(0, int((leader_right - leader_x) // dot_width))

    draw.text((key_x, y), key, font=FONT_15_BOLD, fill=ORANGE)
    draw.text((leader_x, y), "." * dot_count, font=FONT_15_BOLD, fill=FAINT)
    draw.text((value_x, y), value, font=FONT_15_BOLD, fill=LIGHT_BLUE)


def draw_base_card() -> Image.Image:
    frame = Image.new("RGB", (WIDTH, HEIGHT), PAGE_BG)
    draw = ImageDraw.Draw(frame)

    draw.rounded_rectangle((1, 1, 1198, 518), radius=21, fill=BG, outline=BORDER, width=2)
    draw.rounded_rectangle((2, 2, 1197, 56), radius=19, fill=PANEL)
    draw.rectangle((2, 27, 1197, 55), fill=PANEL)
    draw.line((2, 55, 1197, 55), fill=BORDER)

    for x in range(468, 1180, 24):
        draw.line((x, 56, x, 500), fill=GRID)
    for y in range(67, 501, 24):
        draw.line((456, y, 1178, y), fill=GRID)

    draw.ellipse((21, 21, 35, 35), fill="#ff5f56")
    draw.ellipse((45, 21, 59, 35), fill="#ffbd2e")
    draw.ellipse((69, 21, 83, 35), fill="#27c93f")
    draw.text((104, 18), "profile-terminal — shashank@github", font=FONT_16, fill=MUTED)

    draw.text((495, 77), "$", font=FONT_17, fill=GREEN)
    draw.text((518, 77), "whoami --verbose", font=FONT_17, fill=TEXT)
    draw.text((495, 107), "shashank@padavalkar", font=FONT_25_BOLD, fill=WHITE)
    draw.line((495, 145, 1168, 145), fill=BORDER)

    draw_profile_row(draw, 164, "Role", "ML & Computer Vision Engineer")
    draw_profile_row(draw, 196, "Based in", "Karnataka, India")
    draw_profile_row(draw, 228, "Focus", "Deep Learning · Visual Computing")

    draw.text((495, 269), "— Stack", font=FONT_16, fill=TEXT)
    draw.line((575, 277, 1168, 277), fill=BORDER)
    draw_profile_row(draw, 300, "Languages", "Python · C · C++")
    draw_profile_row(draw, 332, "ML / CV", "PyTorch · TensorFlow · OpenCV · scikit-learn")
    draw_profile_row(draw, 364, "Tooling", "AWS · Docker · Linux · Git · PostgreSQL")

    draw.text((495, 405), "— Connect", font=FONT_16, fill=TEXT)
    draw.line((590, 413, 1168, 413), fill=BORDER)
    draw_profile_row(draw, 429, "GitHub", "Shashank-Padavalkar")
    draw_profile_row(draw, 457, "LinkedIn", "shashank-padavalkar")
    draw_profile_row(draw, 485, "Email", "shashankp1307@gmail.com")

    draw.rounded_rectangle((1, 1, 1198, 518), radius=21, outline=BORDER, width=2)
    return frame


def reset_left_pane(base: Image.Image) -> Image.Image:
    frame = base.convert("RGB").copy()

    pane = Image.new("RGB", (WIDTH, HEIGHT), BG)
    pane_draw = ImageDraw.Draw(pane)
    for y in range(55, 519):
        amount = (y - 55) / 464
        color = blend(BG, BG_ALT, amount)
        pane_draw.line((0, y, 455, y), fill=color)

    for x in range(12, 456, 24):
        pane_draw.line((x, 55, x, 518), fill=GRID, width=1)
    for y in range(67, 519, 24):
        pane_draw.line((2, y, 455, y), fill=GRID, width=1)

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
    draw.ellipse((x - radius * 2, y - radius * 2, x + radius * 2, y + radius * 2), outline=FAINT, width=1)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=WHITE)


def draw_dotted_row(
    draw: ImageDraw.ImageDraw,
    y: int,
    key: str,
    value: str,
    *,
    value_color: str | None = None,
) -> None:
    draw.text((22, y), key, font=FONT_12, fill=ORANGE)
    draw.text((112, y), "." * 10, font=FONT_12, fill=FAINT)
    draw.text((205, y), value, font=FONT_12, fill=value_color or LIGHT_BLUE)


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
            fill = SURFACE_ALT if not active else CELL_ACTIVE
            outline = CELL_EDGE
            if row == scan_row:
                fill = LIGHT_BLUE if active else SCAN_OFF
                outline = BLUE
            draw.rectangle((x, y, x + cell, y + cell), fill=fill, outline=outline)

    return origin_x + 8 * (cell + gap), origin_y + 4 * (cell + gap)


def draw_feature_maps(draw: ImageDraw.ImageDraw, activation: float) -> tuple[float, float]:
    x, y = 137, 145
    for layer in range(3, -1, -1):
        offset = layer * 5
        shade = FEATURE_BACK if layer else FEATURE_FRONT
        edge = BLUE if activation > 0.45 and layer == 0 else FEATURE_EDGE
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
                fill=BLUE if lit else FEATURE_CELL,
                outline=FEATURE_CELL_EDGE,
            )
    return x + 73, y + 43


def draw_embedding(draw: ImageDraw.ImageDraw, activation: float) -> tuple[float, float]:
    x = 271
    ys = [149, 166, 183, 200, 217, 234]
    for index, y in enumerate(ys):
        node_activation = phase(activation, index / 8, (index + 2) / 8)
        radius = 5
        fill = GREEN if node_activation > 0.55 else NODE_OFF
        outline = NODE_ACTIVE_EDGE if node_activation > 0.25 else NODE_EDGE
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill, outline=outline)
    return x + 7, sum(ys) / len(ys)


def draw_output(draw: ImageDraw.ImageDraw, activation: float) -> tuple[float, float]:
    x, y, width, height = 321, 143, 116, 98
    edge = GREEN if activation > 0.75 else FEATURE_EDGE
    draw.rounded_rectangle((x, y, x + width, y + height), radius=5, fill=SURFACE, outline=edge)
    draw.text((x + 10, y + 9), "CLASSIFIER", font=FONT_11, fill=TEXT)

    person_value = 0.998 * activation
    other_value = max(0.002 * activation, 0.0)
    bars = (("person", person_value, GREEN), ("other", other_value, FAINT))
    for index, (label, value, color) in enumerate(bars):
        row_y = y + 35 + index * 27
        draw.text((x + 9, row_y), label, font=FONT_11, fill=LIGHT_BLUE)
        bar_x = x + 57
        draw.rectangle((bar_x, row_y + 3, bar_x + 43, row_y + 11), fill=SURFACE_ALT, outline=PANEL_EDGE)
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
    draw.text((371, 78), f"{index + 1:02d}/{FRAME_COUNT}", font=FONT_11, fill=FAINT)

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
        draw.line((*start, *end), fill=TRACE, width=1)

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
    draw_dotted_row(draw, 398, "prediction", prediction, value_color=GREEN if output_activation > 0.9 else FAINT)

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
    draw.rounded_rectangle((20, 443, 437, 487), radius=5, fill=SURFACE, outline=PANEL_EDGE)
    draw.text((31, 453), "backend", font=FONT_11, fill=ORANGE)
    draw.text((94, 453), "PyTorch", font=FONT_11, fill=LIGHT_BLUE)
    draw.text((171, 453), "batch", font=FONT_11, fill=ORANGE)
    draw.text((235, 453), "1", font=FONT_11, fill=LIGHT_BLUE)
    draw.text((306, 453), "status", font=FONT_11, fill=ORANGE)
    draw.text((348, 453), status, font=FONT_11, fill=GREEN if status == "INFERENCE_OK" else LIGHT_BLUE)

    return frame


def pin_gif_matte(gif_path: Path, matte: tuple[int, int, int]) -> None:
    """Set the GIF global palette entry used by the outer corners exactly."""
    with Image.open(gif_path) as image:
        image.seek(0)
        if image.mode != "P":
            raise ValueError(f"Expected a paletted GIF, got {image.mode}: {gif_path}")
        matte_index = image.getpixel((0, 0))

    data = bytearray(gif_path.read_bytes())
    if data[:6] not in (b"GIF87a", b"GIF89a"):
        raise ValueError(f"Not a GIF file: {gif_path}")
    if not data[10] & 0x80:
        raise ValueError(f"GIF has no global color table: {gif_path}")

    color_offset = 13 + matte_index * 3
    data[color_offset : color_offset + 3] = bytes(matte)
    gif_path.write_bytes(data)


def render_theme(theme_name: str) -> None:
    use_theme(theme_name)
    gif_path = ASSETS / f"profile-terminal-{theme_name}.gif"
    png_path = ASSETS / f"profile-terminal-{theme_name}.png"

    base = draw_base_card()
    clean_base = reset_left_pane(base)
    frames = [draw_pipeline(clean_base.copy(), index) for index in range(FRAME_COUNT)]

    completed_frame = 35
    palette_source = frames[completed_frame].quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    matte_index = palette_source.getpixel((0, 0))
    palette = palette_source.getpalette()
    matte_rgb = hex_rgb(PAGE_BG)
    palette[matte_index * 3 : matte_index * 3 + 3] = list(matte_rgb)
    palette_source.putpalette(palette)
    gif_frames = [
        frame.quantize(palette=palette_source, dither=Image.Dither.NONE)
        for frame in frames
    ]
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=False,
        disposal=1,
    )
    pin_gif_matte(gif_path, matte_rgb)

    frames[completed_frame].save(png_path, format="PNG", optimize=True)
    print(f"Rendered {gif_path} ({gif_path.stat().st_size:,} bytes)")
    print(f"Rendered {png_path} ({png_path.stat().st_size:,} bytes)")


def render() -> None:
    for theme_name in THEMES:
        render_theme(theme_name)


if __name__ == "__main__":
    render()
