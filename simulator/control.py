"""Apply frozen K8 control signals to the simulator datapath."""

from simulator.datapath import Datapath
from tools.control_word import encode

OUTPUTS = {
    "A_OUT": "a",
    "X_OUT": "x",
    "Y_OUT": "y",
    "SP_OUT": "sp",
    "MDR_OUT": "mdr",
    "TMP_OUT": "tmp",
}

LOADS = {
    "A_LOAD": "a",
    "X_LOAD": "x",
    "Y_LOAD": "y",
    "SP_LOAD": "sp",
    "IR_LOAD": "ir",
    "MDR_LOAD": "mdr",
    "TMP_LOAD": "tmp",
}

ALU_OPS = {
    "ALU_ADD": "ADD",
    "ALU_SUB": "SUB",
    "ALU_AND": "AND",
    "ALU_OR": "OR",
    "ALU_XOR": "XOR",
}


class ControlError(ValueError):
    pass


def apply_controls(dp: Datapath, signals) -> None:
    """Apply one validated logical control word to the datapath.

    Memory, AGU and sequencer effects are intentionally handled by their own
    simulator components. This function owns direct datapath effects only.
    """

    signals = tuple(signals)
    encode(signals)  # canonical frozen-control validation
    dp.begin_cycle()
    dp.active_controls = signals

    for signal, attr in OUTPUTS.items():
        if signal in signals:
            reg = getattr(dp, attr)
            dp.data_bus.drive(signal, reg.output())

    alu_signals = [s for s in ALU_OPS if s in signals]
    if alu_signals:
        op = ALU_OPS[alu_signals[0]]
        dp.alu.a = dp.a.value
        dp.alu.b = dp.tmp.value
        carry = dp.flags.value & 0x01
        dp.alu.evaluate(op, carry)
    if "ALU_OUT_ENABLE" in signals:
        dp.data_bus.drive("ALU_OUT_ENABLE", dp.alu.result)

    if "PC_TO_MAR" in signals:
        dp.mar.load(dp.pc.output())
    if "SP_TO_MAR" in signals:
        dp.mar.load(0x0100 | dp.sp.output())

    if "PC_INC" in signals:
        dp.pc.load(dp.pc.value + 1)
    if "SP_INC" in signals:
        dp.sp.load(dp.sp.value + 1)
    if "SP_DEC" in signals:
        dp.sp.load(dp.sp.value - 1)

    bus_loads = set(LOADS) | {"PC_LOAD_LO", "PC_LOAD_HI", "MAR_LOAD_LO", "MAR_LOAD_HI"}
    if signals and any(s in signals for s in bus_loads) and dp.data_bus.value is None:
        # MDR_LOAD may later be sourced by the memory component rather than DB.
        if not (set(signals) & bus_loads == {"MDR_LOAD"} and "MEM_READ" in signals):
            raise ControlError("control word requests a bus load with no DB driver")

    if dp.data_bus.value is not None:
        for signal, attr in LOADS.items():
            if signal in signals:
                getattr(dp, attr).load(dp.data_bus.value)
        if "PC_LOAD_LO" in signals:
            dp.pc.load_low(dp.data_bus.value)
        if "PC_LOAD_HI" in signals:
            dp.pc.load_high(dp.data_bus.value)
        if "MAR_LOAD_LO" in signals:
            dp.mar.load_low(dp.data_bus.value)
        if "MAR_LOAD_HI" in signals:
            dp.mar.load_high(dp.data_bus.value)

    # Direct architectural flag-latch controls.
    if "C_SET" in signals:
        dp.flags.load(dp.flags.value | 0x01)
    if "C_CLEAR" in signals:
        dp.flags.load(dp.flags.value & ~0x01)
    if "I_SET" in signals:
        dp.flags.load(dp.flags.value | 0x10)
    if "I_CLEAR" in signals:
        dp.flags.load(dp.flags.value & ~0x10)
    if "V_CLEAR" in signals:
        dp.flags.load(dp.flags.value & ~0x40)
