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
    "ALU_NOT": "NOT",
    "ALU_SHL": "SHL",
    "ALU_SHR": "SHR",
    "ALU_ROL": "ROL",
    "ALU_ROR": "ROR",
}


class ControlError(ValueError):
    pass


def apply_controls(dp: Datapath, signals, *, agu_index_select: int = 0) -> None:
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
    # PC_TO_MAR/SP_TO_MAR are direct 16-bit transfers; accompanying MAR_LOAD
    # strobes do not require an 8-bit DB source.
    direct_mar = "PC_TO_MAR" in signals or "SP_TO_MAR" in signals
    if direct_mar:
        bus_loads -= {"MAR_LOAD_LO", "MAR_LOAD_HI"}
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

    # FLAGS_LATCH updates Z/N from the value visible on DB. For ALU operations
    # it also latches the ALU carry/overflow result. Other flag bits survive.
    if "FLAGS_LATCH" in signals and dp.data_bus.value is not None:
        value = dp.data_bus.value & 0xFF
        flags = dp.flags.value & ~(0x02 | 0x04)
        if value == 0:
            flags |= 0x02
        if value & 0x80:
            flags |= 0x04
        if alu_signals:
            flags &= ~(0x01 | 0x08)
            if dp.alu.carry_out:
                flags |= 0x01
            if dp.alu.overflow:
                flags |= 0x08
        dp.flags.load(flags)

    # Address-generation unit. Index selection is decoded from the opcode and
    # supplied separately from the frozen 48-bit control word.
    if agu_index_select not in (0, 1, 2):
        raise ControlError("reserved AGU index selector")
    dp.agu_index_select = agu_index_select
    dp.agu_index_value = 0 if agu_index_select == 0 else (
        dp.x.value if agu_index_select == 1 else dp.y.value
    )
    clear_aguc_after = "AGUC_CLEAR" in signals
    if "AGU_ADD_LO" in signals:
        low = dp.mar.value & 0xFF
        raw = low + dp.agu_index_value
        dp.agu_low_input = low
        dp.agu_low_result = raw & 0xFF
        dp.mar.load_low(dp.agu_low_result)
        if "AGUC_LOAD" in signals:
            dp.aguc = int(raw > 0xFF)
    elif "AGUC_LOAD" in signals:
        raise ControlError("AGUC_LOAD requires AGU_ADD_LO")
    if "AGU_ADD_HI" in signals:
        dp.mar.load_high(((dp.mar.value >> 8) + dp.aguc) & 0xFF)
    if clear_aguc_after:
        dp.aguc = 0

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
        dp.flags.load(dp.flags.value & ~0x08)
