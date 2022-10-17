import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import User
from accounts.views import (
    DecoratedTokenObtainPairView,
    PublicUserProfileView,
    UserExistsView,
    UserProfileView,
    UserRegisterView,
)

User: User = get_user_model()


class AccountRegisterApiTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_user_can_create_account(self):
        request = self.factory.post(
            "/api/accounts/users",
            {
                "username": "test",
                "password": "test",
                "email": "test@test.com",
                "first_name": "test",
            },
            format="json",
        )
        response = UserRegisterView.as_view()(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue("refresh" in response.data)
        self.assertTrue("access" in response.data)
        get_user = User.objects.get(username="test")
        self.assertEqual(get_user.avatar, User.generate_avatar("test@test.com"))
        self.assertEqual(str(get_user), "test")


class AccountsApiTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="test", password="test", email="test@test.com", first_name="test"
        )

    def test_user_exists_by_username(self):
        request = self.factory.get(f"/api/accounts/user/exists?username={self.user.username}", format="json")
        response = UserExistsView.as_view()(request)
        self.assertEqual(response.status_code, 204 )

    def test_user_exists_by_email(self):
        request = self.factory.get(f"/api/accounts/user/exists?email={self.user.email}", format="json")
        response = UserExistsView.as_view()(request)
        self.assertEqual(response.status_code, 204 )

    def test_user_exits_false(self):
        request = self.factory.get(f"/api/accounts/user/exists?username=notfound", format="json")
        response = UserExistsView.as_view()(request)
        self.assertEqual(response.status_code, 404)

    def test_user_exists_no_username_or_email_provided(self):
        request = self.factory.get(f"/api/accounts/user/exists", format="json")
        response = UserExistsView.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Provide either username or email")


    def test_user_can_login(self):
        request = self.factory.post(
            "/api/accounts/login",
            {"username": "test", "password": "test"},
            format="json",
        )
        view = DecoratedTokenObtainPairView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("refresh" in response.data)
        self.assertTrue("access" in response.data)

    def test_user_get_profile_view(self):
        request = self.factory.get("/api/accounts/user/profile", format="json")
        force_authenticate(request, user=self.user)
        response = UserProfileView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["first_name"], self.user.first_name)
        self.assertEqual(response.data["last_name"], self.user.last_name)
        self.assertEqual(response.data["avatar"], self.user.avatar)

    def test_get_public_profile(self):
        request = self.factory.get(f"/api/accounts/user/{self.user.id}", format="json")
        force_authenticate(request, user=self.user)
        response = PublicUserProfileView.as_view()(request, pk=self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["first_name"], self.user.first_name)
        self.assertEqual(response.data["last_name"], self.user.last_name)
        self.assertEqual(response.data["avatar"], self.user.avatar)

    def test_get_public_profile_not_found(self):
        request = self.factory.get("/api/accounts/user/999", format="json")
        force_authenticate(request, user=self.user)
        response = PublicUserProfileView.as_view()(request, pk=999)
        self.assertEqual(response.status_code, 404)

    def test_get_public_profile_with_show_email_false(self):
        request = self.factory.get(f"/api/accounts/user/{self.user.id}", format="json")
        force_authenticate(request, user=self.user)
        response = PublicUserProfileView.as_view()(request, pk=self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], None)

    def test_get_public_profile_with_show_email_true(self):
        self.user.show_email = True
        self.user.save()
        request = self.factory.get(f"/api/accounts/user/{self.user.id}", format="json")
        force_authenticate(request, user=self.user)
        response = PublicUserProfileView.as_view()(request, pk=self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.user.email)


class ProfileUpdateTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="test", password="test", email="test@test.com", first_name="test"
        )

    def make_request(self, data):
        request = self.factory.patch("/api/accounts/user/profile", data, format="json")
        force_authenticate(request, user=self.user)
        return UserProfileView.as_view()(request)

    def test_user_can_change_avatar(self):
        """
        test user can change avatar
        """
        response = self.make_request({"avatar": User.generate_avatar("something")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["avatar"], User.generate_avatar("something"))

    def test_user_can_change_username(self):
        response = self.make_request({"username": "test1"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "test1")

    def test_user_can_change_email(self):
        response = self.make_request({"email": "test1@test.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "test1@test.com")

    def test_user_can_change_first_name(self):
        response = self.make_request({"first_name": "test1"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "test1")

    def test_user_can_change_last_name(self):
        response = self.make_request({"last_name": "test1"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["last_name"], "test1")

    def test_user_can_change_password(self):
        response = self.make_request({"password": "test1"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user.check_password("test1"))
