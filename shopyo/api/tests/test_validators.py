import pytest

from shopyo.api import validators


class TestValidators:
    """Tests validator methods"""

    @pytest.mark.parametrize(
        "url,expected",
        [
            ("google", False),
            ("www.google.com", True),
            ("https://www.google.com", True),
            ("localhost:3000", True),
            ("192.168.0.250", True),
            ("2001:0db8:85a3:0000:0000:8a2e:0370:7334", True),
        ],
    )
    def test_is_valid_url(self, url, expected):
        result = validators.is_valid_url(url)
        assert result == expected

    @pytest.mark.parametrize(
        "string,expected",
        [
            ("efwfwefwefwef", True),
            ("wehfbweur76tr46348tr", True),
            ("uwfehbuweify2874gr34_____________", True),
            ("^uefew.", False),
            ("wefwfwe/wfwefewf/ewfwef", False),
            ("""%^$^$£%£""£%"£""", False),
            ("""%^$^$£%£""£%"£__""", False),
            ("""%^$^$£%£""£%"£wdwqdqwd__""", False),
            ("""%^$^$£%£""£%"£423423423""", False),
        ],
    )
    def test_is_alpha_num_underscore(self, string, expected):
        result = validators.is_alpha_num_underscore(string)
        assert result == expected

    @pytest.mark.parametrize(
        "string,expected",
        [(" ", True), ("", True), (" adqwd", False), ("wefwefwef", False)],
    )
    def test_is_empty_str(self, string, expected):
        result = validators.is_empty_str(string)
        assert result == expected

    @pytest.mark.parametrize(
        "string,expected",
        [
            ("wefwf-wfwefwef-wefwef", True),
            ("-wefwef-ewfwef-wefwef-wefwef", True),
            ("-wefefwef-", True),
            ("-w6ef78wef687ewf6-wefwef-", True),
            ("---", True),
            ("/efiewf/", False),
            ("(ewfewf)", False),
        ],
    )
    def test_is_valid_slug(self, string, expected):
        result = validators.is_valid_slug(string)
        assert bool(result) == expected
