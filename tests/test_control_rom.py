from tools.generate_control_rom import build_image, address, IMAGE_SIZE, WORD_BYTES
from tools.control_word import encode, bytes_le

def word(image, opcode, step, condition=0):
    p=address(opcode,step,condition)
    return image[p:p+WORD_BYTES]

def test_image_size():
    assert len(build_image()) == IMAGE_SIZE == 98304

def test_nop_fetch_and_finish():
    image=build_image()
    assert word(image,0x00,0) == bytes_le(encode(["PC_TO_MAR","MAR_LOAD_LO","MAR_LOAD_HI"]))
    assert word(image,0x00,3) == bytes_le(encode(["INSTR_DONE"]))

def test_lda_immediate_execution():
    image=build_image()
    expected=encode(["MDR_OUT","A_LOAD","PC_INC","FLAGS_LATCH","INSTR_DONE"])
    assert word(image,0x10,5) == bytes_le(expected)

def test_undefined_opcode_is_zero():
    image=build_image()
    assert word(image,0xFF,0) == bytes(WORD_BYTES)

def test_condition_pages_identical_until_conditions_are_defined():
    image=build_image()
    assert word(image,0x40,5,0) == word(image,0x40,5,3)
