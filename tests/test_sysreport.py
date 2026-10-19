import pytest

from sysreport import check_disk, evaluate


@pytest.mark.parametrize("api_ok,disk_ok,expected", [
    (True, True, 0),
    (False, True, 1),
    (True, False, 1),
])
def test_evaluate(api_ok, disk_ok, expected):
    checks = {"api": {"ok": api_ok}, "disk": {"ok": disk_ok}}
    assert evaluate(checks) == expected


def test_disk_limit_zero_always_fails():
    assert check_disk("/", 0)["ok"] is False
