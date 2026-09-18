from tools.microcode_patterns import immediate8, zero_page_address, absolute_address

def test_immediate8_steps():
    p = immediate8()
    assert [x["step"] for x in p] == [3, 4]
    assert "PC_OUT" in p[0]["signals"]
    assert "MEM_READ" in p[1]["signals"]

def test_zero_page_is_explicit():
    p = zero_page_address()
    assert [x["step"] for x in p] == [3, 4, 5]
    assert p[-1]["signals"] == ["MDR_OUT", "MAR_IN_LO"]

def test_absolute_keeps_both_address_bytes_visible():
    p = absolute_address()
    assert len(p) == 7
    assert "TMP_IN" in p[2]["signals"]
    assert p[-2]["signals"] == ["TMP_OUT", "MAR_IN_LO"]
    assert p[-1]["signals"] == ["MDR_OUT", "MAR_IN_HI"]
