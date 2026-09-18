import json
from pathlib import Path
from tools.check_microcode_coverage import report

def test_coverage_report_matches_isa():
    r=report()
    isa=json.loads(Path("spec/isa.json").read_text())
    micro=json.loads(Path("spec/microcode.json").read_text())
    defined={row[0] for row in isa["instructions"]}
    implemented=set(micro["opcodes"])
    assert r["defined"] == len(defined)
    assert r["microcoded"] == len(defined & implemented)
    assert not r["unknown"]
    assert set(r["missing"]) == defined - implemented
