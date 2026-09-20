"""Shared architectural conformance vectors for K8 implementations."""

VECTORS = [
    {
        "name": "nop",
        "image": [0x00],
        "initial": {},
        "expected": {"pc": 0x8001},
    },
    {
        "name": "ldx_imm",
        "image": [0x18, 0x7E],
        "initial": {},
        "expected": {"x": 0x7E, "pc": 0x8002},
    },
    {
        "name": "ldy_imm",
        "image": [0x20, 0x33],
        "initial": {},
        "expected": {"y": 0x33, "pc": 0x8002},
    },
    {
        "name": "lda_imm",
        "image": [0x10, 0x42],
        "initial": {},
        "expected": {"a": 0x42, "pc": 0x8002},
    },,
    {"name":"tax","image":[0x94],"initial":{"a":0x42},"expected":{"x":0x42,"pc":0x8001}},
    {"name":"tay","image":[0x95],"initial":{"a":0x31},"expected":{"y":0x31,"pc":0x8001}},
    {"name":"txa","image":[0x96],"initial":{"x":0x77},"expected":{"a":0x77,"pc":0x8001}},
    {"name":"tya","image":[0x97],"initial":{"y":0x55},"expected":{"a":0x55,"pc":0x8001}},
]
