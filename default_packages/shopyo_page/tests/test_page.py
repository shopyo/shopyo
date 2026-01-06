import unittest
from shopyo.app import create_app
from shopyo.api.models import db
from shopyo_page.models import Page
from shopyo_i18n.models import LangRecord
import os


class TestShopyoPage(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.app.config["DEBUG"] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        # Add a default language for testing
        lang = LangRecord(lang_code="en", lang_name="English")
        db.session.add(lang)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post(
            "/auth/login",
            data=dict(email=email, password=password),
            follow_redirects=True,
        )

    def logout(self):
        return self.client.get("/auth/logout", follow_redirects=True)

    def create_admin_user(self):
        # Assuming there's a way to create an admin user for testing
        # This might involve creating a User model and assigning admin role
        pass

    def test_create_page(self):
        self.create_admin_user()
        self.login("admin@example.com", "password")
        response = self.client.post(
            "/page/check_pagecontent",
            data={
                "title": "Test Page",
                "slug": "test-page",
                "content": "<p>This is a test page.</p>",
                "meta_description": "A test meta description",
                "meta_keywords": "test, page, keywords",
                "lang": "en",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        page = Page.query.filter_by(slug="test-page").first()
        self.assertIsNotNone(page)
        self.assertEqual(page.title, "Test Page")
        self.assertEqual(page.meta_description, "A test meta description")
        self.assertEqual(page.meta_keywords, "test, page, keywords")
        self.assertEqual(page.get_content(), "<p>This is a test page.</p>")

    def test_edit_page(self):
        self.create_admin_user()
        self.login("admin@example.com", "password")
        # Create a page first
        self.client.post(
            "/page/check_pagecontent",
            data={
                "title": "Original Page",
                "slug": "original-page",
                "content": "<p>Original content.</p>",
                "meta_description": "Original meta description",
                "meta_keywords": "original, page",
                "lang": "en",
            },
            follow_redirects=True,
        )
        page = Page.query.filter_by(slug="original-page").first()

        response = self.client.post(
            "/page/edit_pagecontent",
            data={
                "page_id": page.id,
                "title": "Updated Page",
                "slug": "updated-page",
                "content": "<p>Updated content.</p>",
                "meta_description": "Updated meta description",
                "meta_keywords": "updated, page",
                "lang": "en",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        updated_page = Page.query.filter_by(slug="updated-page").first()
        self.assertIsNotNone(updated_page)
        self.assertEqual(updated_page.title, "Updated Page")
        self.assertEqual(updated_page.meta_description, "Updated meta description")
        self.assertEqual(updated_page.meta_keywords, "updated, page")
        self.assertEqual(updated_page.get_content(), "<p>Updated content.</p>")

    def test_upload_image(self):
        self.create_admin_user()
        self.login("admin@example.com", "password")

        # Create a dummy image file
        dummy_image_path = os.path.join(self.app.root_path, "dummy_image.png")
        with open(dummy_image_path, "wb") as f:
            f.write(b"dummy_image_content")

        with open(dummy_image_path, "rb") as img:
            response = self.client.post(
                "/page/upload_image",
                data={"file": (img, "dummy_image.png")},
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"location", response.data)
        self.assertIn(b"dummy_image.png", response.data)

        # Clean up the dummy image file
        os.remove(dummy_image_path)

    def test_page_revisions(self):
        self.create_admin_user()
        self.login("admin@example.com", "password")

        # Create a page
        self.client.post(
            "/page/check_pagecontent",
            data={
                "title": "Revision Test Page",
                "slug": "revision-test-page",
                "content": "<p>Initial content.</p>",
                "meta_description": "Initial meta description",
                "meta_keywords": "initial, keywords",
                "lang": "en",
            },
            follow_redirects=True,
        )
        page = Page.query.filter_by(slug="revision-test-page").first()

        # Edit the page multiple times to create revisions
        self.client.post(
            "/page/edit_pagecontent",
            data={
                "page_id": page.id,
                "title": "Revision Test Page",
                "slug": "revision-test-page",
                "content": "<p>Second content.</p>",
                "meta_description": "Second meta description",
                "meta_keywords": "second, keywords",
                "lang": "en",
            },
            follow_redirects=True,
        )

        self.client.post(
            "/page/edit_pagecontent",
            data={
                "page_id": page.id,
                "title": "Revision Test Page",
                "slug": "revision-test-page",
                "content": "<p>Third content.</p>",
                "meta_description": "Third meta description",
                "meta_keywords": "third, keywords",
                "lang": "en",
            },
            follow_redirects=True,
        )

        response = self.client.get(f"/page/dashboard/s/{page.slug}/revisions")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Initial content.", response.data)
        self.assertIn(b"Second content.", response.data)
        self.assertIn(b"Third content.", response.data)

    def test_revert_page_revision(self):
        self.create_admin_user()
        self.login("admin@example.com", "password")

        # Create a page
        self.client.post(
            "/page/check_pagecontent",
            data={
                "title": "Revert Test Page",
                "slug": "revert-test-page",
                "content": "<p>Original content.</p>",
                "meta_description": "Original meta description",
                "meta_keywords": "original, keywords",
                "lang": "en",
            },
            follow_redirects=True,
        )
        page = Page.query.filter_by(slug="revert-test-page").first()

        # Edit the page to create a revision
        self.client.post(
            "/page/edit_pagecontent",
            data={
                "page_id": page.id,
                "title": "Revert Test Page",
                "slug": "revert-test-page",
                "content": "<p>Updated content.</p>",
                "meta_description": "Updated meta description",
                "meta_keywords": "updated, keywords",
                "lang": "en",
            },
            follow_redirects=True,
        )

        # Get the original revision ID
        original_revision = page.revisions[-2]  # Assuming at least two revisions now

        # Revert to the original revision
        response = self.client.post(
            f"/page/revert/{original_revision.id}", follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

        reverted_page = Page.query.filter_by(slug="revert-test-page").first()
        self.assertEqual(reverted_page.get_content(), "<p>Original content.</p>")
        self.assertEqual(reverted_page.meta_description, "Original meta description")
        self.assertEqual(reverted_page.meta_keywords, "original, keywords")


if __name__ == "__main__":
    unittest.main()
