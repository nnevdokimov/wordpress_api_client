import unittest

from wordpress_api_client.client import WordpressClient

BASE_URL = "https://example.com"
LOGIN = "your_login"
PASSWORD = "your_password"


class TestWordpressClient(unittest.TestCase):
    def setUp(self):
        self.client = WordpressClient(BASE_URL, LOGIN, PASSWORD)

    def test_create_post(self):
        response = self.client.create_post(title="Test Post",
                                           content="This is a test",
                                           status="draft")
        self.assertIn("id", response)

    def test_get_post(self):
        post_id = 1
        response = self.client.get_post(post_id=post_id)
        self.assertEqual(response["id"], post_id)

    def test_update_post(self):
        post_id = 1
        response = self.client.update_post(post_id=post_id,
                                           title="Updated Title")
        self.assertEqual(response["title"]["rendered"], "Updated Title")

    def test_delete_post(self):
        post_id = 1
        response = self.client.delete_post(post_id=post_id)
        self.assertIn("deleted", response)


if __name__ == "__main__":
    unittest.main()
