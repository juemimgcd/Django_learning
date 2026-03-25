from rest_framework.test import APITestCase

from .models import User, UserLoginLog, UserToken


class UserApiTests(APITestCase):
    def test_register_returns_token_and_user_info(self):
        response = self.client.post(
            "/api/user/register",
            {"username": "alice", "password": "secret123"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["code"], 200)
        self.assertEqual(response.data["data"]["userInfo"]["username"], "alice")
        self.assertIn("token", response.data["data"])
        self.assertTrue(User.objects.filter(username="alice").exists())
        self.assertTrue(UserToken.objects.filter(user__username="alice").exists())
        self.assertTrue(UserLoginLog.objects.filter(user__username="alice").exists())

    def test_duplicate_username_register_fails(self):
        User.objects.create_user(username="alice", password="secret123")

        response = self.client.post(
            "/api/user/register",
            {"username": "alice", "password": "secret123"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)

    def test_login_returns_token(self):
        User.objects.create_user(username="alice", password="secret123")

        response = self.client.post(
            "/api/user/login",
            {"username": "alice", "password": "secret123"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["userInfo"]["username"], "alice")
        self.assertIn("token", response.data["data"])

    def test_login_with_wrong_password_fails(self):
        User.objects.create_user(username="alice", password="secret123")

        response = self.client.post(
            "/api/user/login",
            {"username": "alice", "password": "wrong123"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_info_requires_token(self):
        response = self.client.get("/api/user/info")
        self.assertEqual(response.status_code, 401)

    def test_info_update_and_password_flow(self):
        user = User.objects.create_user(username="alice", password="secret123")
        token_record = UserToken.objects.create(
            user=user,
            token="token-123",
            expires_at=UserToken.default_expiry(),
        )
        auth_header = f"Bearer {token_record.token}"

        info_response = self.client.get("/api/user/info", HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(info_response.status_code, 200)
        self.assertEqual(info_response.data["data"]["username"], "alice")

        update_response = self.client.put(
            "/api/user/update",
            {
                "nickname": "Alice",
                "gender": User.GENDER_FEMALE,
                "bio": "hello",
            },
            format="json",
            HTTP_AUTHORIZATION=auth_header,
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data["data"]["nickname"], "Alice")

        password_response = self.client.put(
            "/api/user/password",
            {
                "oldPassword": "secret123",
                "newPassword": "newsecret123",
            },
            format="json",
            HTTP_AUTHORIZATION=auth_header,
        )
        self.assertEqual(password_response.status_code, 200)

        user.refresh_from_db()
        self.assertTrue(user.check_password("newsecret123"))
