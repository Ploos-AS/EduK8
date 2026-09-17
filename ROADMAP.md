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
- [ ] Evaluate opcode allocation
- [ ] Freeze instruction encoding
- [ ] Freeze calling convention
- [ ] Generate initial conformance vectors
- [ ] Complete architecture review and M1 freeze

## M2 — Reference Emulator
- [ ] Implement CPU state model
- [ ] Implement memory and I/O
- [ ] Implement instruction execution
- [ ] Implement deterministic stepping
- [ ] Implement trace output
- [ ] Implement save/load state
- [ ] Add conformance tests

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
- [ ] Complete emulator
- [ ] Complete toolchain
- [ ] Reproducible builds
- [ ] Release package
