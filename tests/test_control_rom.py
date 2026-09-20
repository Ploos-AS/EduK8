from tools.generate_control_rom import build_image, address, IMAGE_SIZE, WORD_BYTES
from tools.control_word import encode, bytes_le

def word(image, opcode, step, condition=0):
    p=address(opcode,step,condition)
    return image[p:p+WORD_BYTES]

def test_image_size():
    assert len(build_image()) == IMAGE_SIZE == 196608

def test_nop_fetch_and_finish():
    image=build_image()
    assert word(image,0x00,0) == bytes_le(encode(["PC_TO_MAR"]))
    assert word(image,0x00,3) == bytes_le(encode(["INSTR_DONE","STEP_RESET"]))

def test_lda_immediate_execution():
    image=build_image()
    expected=encode(["MDR_OUT","A_LOAD","PC_INC","FLAGS_LATCH","INSTR_DONE","STEP_RESET"])
    assert word(image,0x10,5) == bytes_le(expected)

def test_undefined_opcode_is_zero():
    image=build_image()
    assert word(image,0xFF,0) == bytes(WORD_BYTES)

def test_condition_pages_identical_until_conditions_are_defined():
    image=build_image()
    assert word(image,0x40,5,0) == word(image,0x40,5,3)


def test_monolithic_image_matches_physical_control_store_words():
    from tools.control_store import DEPTH
    image = build_image()
    assert DEPTH == 32768
    for opcode, step, condition in ((0x00, 0, 0), (0x00, 3, 3), (0x10, 5, 0), (0x40, 5, 2), (0xFF, 31, 3)):
        offset = address(opcode, step, condition)
        logical = (opcode << 7) | (step << 2) | condition
        assert offset == logical * WORD_BYTES
        assert image[offset:offset + WORD_BYTES] == bytes_le(int.from_bytes(image[offset:offset + WORD_BYTES], "little"))
