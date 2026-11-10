"""
Tests D2: the uploads route must not read arbitrary files.
"""
import unittest

from app import app


class D2PathTraversalTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_path_traversal_is_rejected(self):
        for name in ["../app.py", "../../etc/passwd", "/etc/passwd", ".env"]:
            response = self.client.get("/uploads/", query_string={"name": name})
            self.assertEqual(response.status_code, 400, name)

    def test_valid_image_still_works(self):
        response = self.client.get("/uploads/", query_string={"name": "room-1.jpg"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[:2], b"\xff\xd8")  # JPEG magic bytes


if __name__ == "__main__":
    unittest.main()
