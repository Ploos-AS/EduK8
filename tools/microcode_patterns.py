"""Inspectable helpers for constructing K8 microcode source."""

def step(number, *signals):
    return {"step": number, "signals": list(signals)}

def immediate8(start=3):
    return [
        step(start, "PC_TO_MAR"),
        step(start + 1, "MEM_READ", "MDR_LOAD"),
    ]

def zero_page_address(start=3):
    return [
        step(start, "PC_TO_MAR"),
        step(start + 1, "MEM_READ", "MDR_LOAD", "PC_INC"),
        step(start + 2, "MDR_OUT", "MAR_LOAD_LO"),
    ]

def absolute_address(start=3):
    return [
        step(start, "PC_TO_MAR"),
        step(start + 1, "MEM_READ", "MDR_LOAD", "PC_INC"),
        step(start + 2, "MDR_OUT", "TMP_LOAD"),
        step(start + 3, "PC_TO_MAR"),
        step(start + 4, "MEM_READ", "MDR_LOAD", "PC_INC"),
        step(start + 5, "TMP_OUT", "MAR_LOAD_LO"),
        step(start + 6, "MDR_OUT", "MAR_LOAD_HI"),
    ]

def read_operand(start):
    return [
        step(start, "MEM_READ", "MDR_LOAD"),
    ]
