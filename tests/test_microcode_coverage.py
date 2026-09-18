from tools.check_microcode_coverage import report

def test_coverage_report_matches_isa():
    r=report()
    assert r["defined"] == 89
    assert r["microcoded"] == 8
    assert not r["unknown"]
    assert "02" in r["missing"]
    assert "97" in r["missing"]
