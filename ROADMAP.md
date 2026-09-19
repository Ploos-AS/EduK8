# EduK8 Roadmap

## M0 — Foundation
- [x] Establish EduK8 identity and tagline
- [x] Define K8 as the physical “Komputer 8 bit”
- [x] Define learning-first architecture goals
- [x] Define repository layout
- [x] Define emulator as the reference model
- [x] Define cross-layer conformance as a core requirement
- [x] Freeze initial project direction

## M1 — K8 Architecture
- [x] Define registers and programmer-visible state
- [x] Define ALU operations and flags
- [x] Define candidate instruction groups
- [x] Define addressing modes
- [x] Define candidate memory map
- [x] Define I/O model
- [x] Define reset/vector behaviour
- [x] Produce architecture reference documents
- [x] Evaluate opcode allocation
- [x] Freeze initial instruction encoding
- [x] Freeze initial calling convention
- [x] Generate initial conformance vectors
- [x] Complete architecture review and M1 freeze

## M2 — Reference Emulator
- [x] Implement CPU state model
- [x] Implement memory and I/O
- [x] Implement instruction execution (core ISA)
- [x] Implement deterministic stepping
- [x] Implement initial instruction/micro-operation trace model
- [x] Define control-unit microstep model and logical control signals
- [x] Define 48-bit control-word layout and safety validator
- [x] Implement save/load state
- [x] Add emulator and portable conformance tests
- [x] Qualify reference emulator against frozen K8 v1 architecture

## M2.5 — K8 Simulator
- [x] Define simulator scope and distinction from the reference emulator
- [ ] Model CPU datapath components, buses and control signals
- [ ] Model clock, reset and microstep/control-store sequencing
- [ ] Simulate memory decode and memory-mapped I/O
- [ ] Visualize registers, ALU, buses, flags and active control lines
- [ ] Support clock-cycle and microstep execution
- [ ] Support interactive switches, LEDs, keyboard, display and GPIO
- [ ] Load K8 binaries and ROM images
- [ ] Cross-check simulator state against reference emulator
- [ ] Run shared architectural conformance vectors
- [ ] Add deterministic simulator tests
- [ ] Document simulator architecture and educational use
- [ ] Qualify simulator against the frozen K8 v1 architecture

## M3 — Assembler
- [ ] Define K8 assembly syntax
- [ ] Implement lexer/parser
- [ ] Implement symbols and labels
- [ ] Implement binary generation
- [ ] Add assembler diagnostics
- [ ] Cross-test against emulator

## M4 — Hardware Prototype
- [ ] KiCad schematics
- [ ] Clock/reset module
- [ ] Registers
- [ ] ALU
- [ ] Control unit
- [ ] Memory
- [ ] I/O
- [ ] PCB
- [ ] BOM
- [ ] Hand-soldering documentation

## M5 — Physical K8 Bring-up
- [ ] Power validation
- [ ] Clock validation
- [ ] Reset validation
- [ ] Register tests
- [ ] ALU tests
- [ ] Memory tests
- [ ] First instruction
- [ ] First program

## M6 — K8 Compiler
- [ ] Educational language specification
- [ ] Lexer/parser
- [ ] AST
- [ ] Semantic analysis
- [ ] K8 IR
- [ ] K8 backend
- [ ] Debug information

## M7 — Debugger and Studio
- [ ] Interactive debugger
- [ ] Register/memory inspection
- [ ] Breakpoints
- [ ] Single-step execution
- [ ] Source-level debugging
- [ ] Visual CPU/bus view
- [ ] Integrated build/run workflow

## M8 — K8 OS
- [ ] Boot process
- [ ] Console
- [ ] Keyboard
- [ ] Memory services
- [ ] Filesystem
- [ ] Basic process/task model

## M9 — Educational Curriculum
- [ ] Electronics lessons
- [ ] Digital logic lessons
- [ ] CPU lessons
- [ ] Assembly lessons
- [ ] Compiler lessons
- [ ] OS lessons
- [ ] Hardware bring-up labs

## M10 — Production Release
- [ ] Final PCB revision
- [ ] Assembly guide
- [ ] User manual
- [ ] Developer manual
- [ ] Complete reference emulator
- [ ] Complete K8 hardware-level simulator
- [ ] Complete toolchain
- [ ] Reproducible builds
- [ ] Release package


## Hardware implementations

### M4 — Dual implementation architecture
- [x] Define K8 Classic discrete-logic implementation
- [x] Define K8 FPGA implementation
- [x] Make emulator the architectural reference
- [ ] Freeze Classic datapath schematic
- [x] Define Clock/reset/single-step architecture
- [ ] Create synthesizable FPGA top-level
- [ ] Establish shared ISA/ROM verification vectors
- [ ] Qualify FPGA against emulator
- [ ] Qualify Classic hardware against emulator
