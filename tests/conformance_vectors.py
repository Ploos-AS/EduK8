"""Shared architectural conformance vectors for K8 implementations."""

VECTORS = [
    {
        "name": "nop",
        "image": [0x00],
        "initial": {},
        "expected": {"pc": 0x8001},
    },
    {
        "name": "lda_imm",
        "image": [0x10, 0x42],
        "initial": {},
        "expected": {"a": 0x42, "pc": 0x8002},
    },
]
