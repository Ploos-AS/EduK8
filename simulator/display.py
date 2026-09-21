"""K8 40x25 text display view backed directly by VRAM."""

VRAM_START = 0x7800
WIDTH = 40
HEIGHT = 25
VISIBLE = WIDTH * HEIGHT


def text_rows(memory) -> list[str]:
    rows = []
    for y in range(HEIGHT):
        cells = bytes(memory.read(VRAM_START + y * WIDTH + x) for x in range(WIDTH))
        rows.append(cells.decode("latin1"))
    return rows


def render_text(memory) -> str:
    return "\n".join(text_rows(memory)) + "\n"


def video_state(memory) -> dict:
    return {
        "control": memory.read(0xC020),
        "status": memory.read(0xC021),
        "cursor_x": memory.read(0xC022) % WIDTH,
        "cursor_y": memory.read(0xC023) % HEIGHT,
        "cursor_control": memory.read(0xC024),
        "border": memory.read(0xC025),
    }


def render_status(memory) -> str:
    v = video_state(memory)
    return (
        f"VIDEO CTRL={v['control']:02X} STATUS={v['status']:02X} "
        f"CURSOR=({v['cursor_x']},{v['cursor_y']}) "
        f"CURSOR_CTRL={v['cursor_control']:02X} BORDER={v['border']:02X}\n"
    )
