from shopyo.api.info import printinfo


def test_printinfo(capsys):
    printinfo()
    captured = capsys.readouterr()
    assert "Framework ©" in captured.out
