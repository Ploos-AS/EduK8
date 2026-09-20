import json

from tools.control_store import DEPTH, build_microcode, slices
from tools.generate_control_rom import WORD_BYTES, build_image


def test_shared_builder_has_canonical_depth():
    source = json.loads(open("spec/microcode.json").read())
    words = build_microcode(source)
    assert DEPTH == 32768
    assert len(words) == DEPTH


def test_shared_builder_reconstructs_monolithic_words():
    source = json.loads(open("spec/microcode.json").read())
    words = build_microcode(source)
    image = build_image()
    for logical in (0, 3, (0x10 << 7) | (5 << 2), (0x94 << 7) | (3 << 2), DEPTH - 1):
        value = words[logical]
        assert image[logical * WORD_BYTES:(logical + 1) * WORD_BYTES] == value.to_bytes(WORD_BYTES, "little")


def test_physical_slices_reconstruct_every_control_word():
    source = json.loads(open("spec/microcode.json").read())
    words = build_microcode(source)
    roms = slices(words)
    assert len(roms) == 6
    assert all(len(rom) == DEPTH for rom in roms)
    for logical, expected in enumerate(words):
        reconstructed = sum(roms[sl][logical] << (8 * sl) for sl in range(6))
        assert reconstructed == expected
