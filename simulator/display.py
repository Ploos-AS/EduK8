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
