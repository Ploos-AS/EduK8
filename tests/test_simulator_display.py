from simulator.core import K8Simulator
from simulator.display import HEIGHT, WIDTH, render_text, text_rows
from simulator.tui import execute


def test_display_renders_40x25_vram(capsys):
    sim = K8Simulator()
    message = b"K8 READY"
    sim.load_image(0x7800, message)

    rows = text_rows(sim.memory)
    assert len(rows) == HEIGHT
    assert all(len(row) == WIDTH for row in rows)
    assert rows[0].startswith("K8 READY")
    assert len(render_text(sim.memory).splitlines()) == HEIGHT

    execute(sim, "display")
    output = capsys.readouterr().out
    assert output.startswith("K8 READY")
    assert len(output.splitlines()) == HEIGHT
