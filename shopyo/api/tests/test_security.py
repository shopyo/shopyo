# import pytest
# from shopyo.api import security
# class TestSecurity:
#     @pytest.mark.parametrize(
#         "url,expected",
#         [
#             ("https://domain.com?next=https://domain.com/somewhere", True),
#             ("https://domain.com?next=ftp://domain.com/somewhere", False),
#         ],
#     )
#     def test_is_safe_redirect_url(self, url, expected):
#         result = security.is_safe_redirect_url(url)
#         assert result == expected
