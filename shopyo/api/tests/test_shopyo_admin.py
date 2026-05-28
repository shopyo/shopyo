import pytest
from flask import Flask
from unittest.mock import MagicMock, patch


@pytest.fixture
def app():
    application = Flask(__name__)
    application.secret_key = "test-key"
    return application


def _make_mock_user(is_authenticated=False, is_admin=False):
    user = MagicMock()
    user.is_authenticated = is_authenticated
    user.is_admin = is_admin
    return user


class TestDefaultModelView:
    def test_is_accessible_authenticated_admin(self, app):
        import shopyo.shopyo_admin as admin_mod

        mock_user = _make_mock_user(is_authenticated=True, is_admin=True)
        with patch.object(admin_mod, "current_user", mock_user):
            view = admin_mod.DefaultModelView.__new__(admin_mod.DefaultModelView)
            assert view.is_accessible() is True

    def test_is_accessible_not_authenticated(self, app):
        import shopyo.shopyo_admin as admin_mod

        mock_user = _make_mock_user(is_authenticated=False, is_admin=False)
        with patch.object(admin_mod, "current_user", mock_user):
            view = admin_mod.DefaultModelView.__new__(admin_mod.DefaultModelView)
            assert view.is_accessible() is False

    def test_is_accessible_authenticated_not_admin(self, app):
        import shopyo.shopyo_admin as admin_mod

        mock_user = _make_mock_user(is_authenticated=True, is_admin=False)
        with patch.object(admin_mod, "current_user", mock_user):
            view = admin_mod.DefaultModelView.__new__(admin_mod.DefaultModelView)
            assert view.is_accessible() is False

    def test_inaccessible_callback_redirects_to_login(self, app):
        with app.test_request_context():
            from shopyo.shopyo_admin import DefaultModelView

            view = DefaultModelView.__new__(DefaultModelView)
            with patch(
                "shopyo.shopyo_admin.url_for", return_value="/auth/login?next=/"
            ) as mock_url_for:
                result = view.inaccessible_callback("list")
                assert result.status_code == 302
                mock_url_for.assert_called_once()


class TestMyAdminIndexView:
    def test_is_accessible_authenticated_admin(self, app):
        import shopyo.shopyo_admin as admin_mod

        mock_user = _make_mock_user(is_authenticated=True, is_admin=True)
        with patch.object(admin_mod, "current_user", mock_user):
            view = admin_mod.MyAdminIndexView.__new__(admin_mod.MyAdminIndexView)
            assert view.is_accessible() is True

    def test_is_accessible_not_authenticated(self, app):
        import shopyo.shopyo_admin as admin_mod

        mock_user = _make_mock_user(is_authenticated=False, is_admin=False)
        with patch.object(admin_mod, "current_user", mock_user):
            view = admin_mod.MyAdminIndexView.__new__(admin_mod.MyAdminIndexView)
            assert view.is_accessible() is False

    def test_inaccessible_callback_redirects_to_login(self, app):
        with app.test_request_context():
            from shopyo.shopyo_admin import MyAdminIndexView

            view = MyAdminIndexView.__new__(MyAdminIndexView)
            with patch(
                "shopyo.shopyo_admin.url_for", return_value="/auth/login?next=/"
            ):
                result = view.inaccessible_callback("index")
                assert result.status_code == 302

    def test_index_unauthenticated_redirects_to_login(self, app):
        with app.test_request_context():
            import shopyo.shopyo_admin as admin_mod

            mock_user = _make_mock_user(is_authenticated=False)
            with patch.object(admin_mod, "current_user", mock_user):
                with patch("shopyo.shopyo_admin.url_for", return_value="/auth/login"):
                    view = admin_mod.MyAdminIndexView.__new__(
                        admin_mod.MyAdminIndexView
                    )
                    result = view.index()
                    assert result.status_code == 302

    def test_index_no_permission_aborts_403(self, app):
        with app.test_request_context():
            import shopyo.shopyo_admin as admin_mod
            from werkzeug.exceptions import Forbidden

            mock_user = _make_mock_user(is_authenticated=True, is_admin=False)
            with patch.object(admin_mod, "current_user", mock_user):
                admin_mod.policy_engine._role_permissions.pop("admin", None)
                admin_mod.policy_engine._policies.clear()
                view = admin_mod.MyAdminIndexView.__new__(admin_mod.MyAdminIndexView)
                for cls in type(view).__mro__:
                    fn = cls.__dict__.get("index")
                    if fn and getattr(fn, "__wrapped__", None):
                        with pytest.raises(Forbidden):
                            fn.__wrapped__(view)
                        break

    def test_index_with_admin_bypass(self, app):
        with app.test_request_context():
            import shopyo.shopyo_admin as admin_mod

            mock_user = _make_mock_user(is_authenticated=True, is_admin=True)
            with patch.object(admin_mod, "current_user", mock_user):
                view = admin_mod.MyAdminIndexView.__new__(admin_mod.MyAdminIndexView)
                for cls in type(view).__mro__:
                    fn = cls.__dict__.get("index")
                    if fn and getattr(fn, "__wrapped__", None):
                        with patch(
                            "flask_admin.AdminIndexView.index", return_value="ok"
                        ):
                            result = fn.__wrapped__(view)
                            assert result == "ok"
                        break
