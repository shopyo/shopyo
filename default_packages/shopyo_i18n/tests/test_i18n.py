import unittest
from shopyo.api.models import db
from shopyo.app import create_app
from shopyo_i18n.models import LangRecord


class Testi18n(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_set_lang(self):
        with self.client as c:
            # Add a language to the database
            lang = LangRecord(lang_code="es", lang_name="Spanish")
            db.session.add(lang)
            db.session.commit()

            # Test setting the language
            response = c.get("/set-lang?lang=es", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            with c.session_transaction() as sess:
                self.assertEqual(sess["yo_current_lang"], "es")

    def test_dashboard(self):
        # This test requires a logged in user, which is outside the scope of this module
        pass


if __name__ == "__main__":
    unittest.main()
