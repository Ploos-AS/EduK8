from simulator.core import K8Simulator
from simulator.display import HEIGHT, WIDTH, render_text, text_rows, video_state, render_status
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
    assert output.startswith("VIDEO CTRL=")\n    assert "K8 READY" in output
    assert len(output.splitlines()) == HEIGHT + 1


def test_video_cursor_mmio_state():
    sim = K8Simulator()
    sim.memory.write(0xC020, 0x01)
    sim.memory.write(0xC021, 0x80)
    sim.memory.write(0xC022, 41)
    sim.memory.write(0xC023, 26)
    sim.memory.write(0xC024, 0x03)
    sim.memory.write(0xC025, 0x07)

    state = video_state(sim.memory)
    assert state == {
        "control": 0x01, "status": 0x80,
        "cursor_x": 1, "cursor_y": 1,
        "cursor_control": 0x03, "border": 0x07,
    }
    assert "CURSOR=(1,1)" in render_status(sim.memory)
