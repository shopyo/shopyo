from unittest.mock import MagicMock, patch
from shopyo.api.forms import flash_errors


def test_flash_errors():
    mock_form = MagicMock()
    mock_form.errors = {"field1": ["error1", "error2"]}
    mock_form.field1.label.text = "Field 1"

    with patch("shopyo.api.forms.flash") as mock_flash:
        with patch(
            "shopyo.api.forms.notify_warning", side_effect=lambda x: x
        ) as mock_notify:
            flash_errors(mock_form)
            assert mock_flash.call_count == 2
            mock_flash.assert_any_call("Error in the Field 1 field - error1")
            mock_flash.assert_any_call("Error in the Field 1 field - error2")
