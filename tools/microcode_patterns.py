"""Inspectable helpers for constructing K8 microcode source."""

def step(number, *signals):
    return {"step": number, "signals": list(signals)}

def immediate8(start=3):
    return [
        step(start, "PC_OUT", "MAR_IN_LO", "MAR_IN_HI"),
        step(start + 1, "MEM_READ", "MDR_IN"),
    ]

def zero_page_address(start=3):
    return [
        step(start, "PC_OUT", "MAR_IN_LO", "MAR_IN_HI"),
        step(start + 1, "MEM_READ", "MDR_IN", "PC_INC"),
        step(start + 2, "MDR_OUT", "MAR_IN_LO"),
    ]

def absolute_address(start=3):
    return [
        step(start, "PC_OUT", "MAR_IN_LO", "MAR_IN_HI"),
        step(start + 1, "MEM_READ", "MDR_IN", "PC_INC"),
        step(start + 2, "MDR_OUT", "TMP_IN"),
        step(start + 3, "PC_OUT", "MAR_IN_LO", "MAR_IN_HI"),
        step(start + 4, "MEM_READ", "MDR_IN", "PC_INC"),
        step(start + 5, "TMP_OUT", "MAR_IN_LO"),
        step(start + 6, "MDR_OUT", "MAR_IN_HI"),
    ]

def read_operand(start):
    return [
        step(start, "MEM_READ", "MDR_IN"),
    ]
