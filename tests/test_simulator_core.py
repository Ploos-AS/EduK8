from simulator.core import K8Simulator


def test_real_fetch_t0_t1_t2_through_integrated_core():
    sim = K8Simulator()
    sim.datapath.pc.load(0x8000)
    sim.load_image(0x8000, bytes([0x10]), force=True)

    assert sim.microstep() == ("PC_TO_MAR", "MAR_LOAD_LO", "MAR_LOAD_HI")
    assert sim.datapath.mar.value == 0x8000
    assert sim.datapath.microstep == 1

    assert sim.microstep() == ("MEM_READ", "MDR_LOAD")
    assert sim.datapath.mdr.value == 0x10
    assert sim.datapath.microstep == 2

    assert sim.microstep() == ("MDR_OUT", "IR_LOAD", "PC_INC")
    assert sim.datapath.ir.value == 0x10
    assert sim.datapath.pc.value == 0x8001
    assert sim.datapath.microstep == 3


def test_clock_rising_edge_executes_microstep():
    sim = K8Simulator()
    sim.datapath.pc.load(0x8123)
    assert sim.clock_step() == 1
    assert sim.datapath.mar.value == 0x8123
    assert sim.datapath.microstep == 1
    assert sim.clock_step() == 0
    assert sim.datapath.microstep == 1


def test_reset_blocks_execution_until_released():
    sim = K8Simulator()
    sim.datapath.pc.load(0x8000)
    sim.reset()
    assert sim.microstep() == ()
    assert sim.datapath.microstep == 0
    sim.release_reset()
    sim.microstep()
    assert sim.datapath.microstep == 1


def test_snapshot_exposes_integrated_machine_state():
    sim = K8Simulator()
    snap = sim.snapshot()
    assert snap["registers"]["SP"] == 0xFF
    assert snap["microstep"] == 0
    assert snap["halted"] is False
    assert snap["condition"] == 0
