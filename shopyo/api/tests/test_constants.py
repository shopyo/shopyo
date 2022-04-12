from shopyo.api import constants


class TestConstants:
    def test_constants(self):
        assert constants.SEP_CHAR == "#"
        assert constants.SEP_NUM == 23
