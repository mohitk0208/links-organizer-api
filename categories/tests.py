import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import User
from categories.models import Category
from categories.views import CategoryViewSet

User: User = get_user_model()

class CategoryCreateApiTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username= "test",
            password="test",
            email="test@test.com",
            first_name="test"
        )

    def test_create_new_category(self):
        request_data = {
            "name": "category1",
            "description": "This is a test category.",
            "background_url": "https://picsum.photos/400"
        }
        request = self.factory.post("/api/categories/",
        request_data,
        format="json"
        )
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], request_data["name"])
        self.assertEqual(response.data["description"], request_data["description"])
        self.assertEqual(response.data["background_url"], request_data["background_url"])
        self.assertEqual(response.data["owner"], self.user.id)
        self.assertEqual(response.data["owner_username"], self.user.username)
        self.assertEqual(response.data["owner_avatar"], self.user.avatar)
        self.assertEqual(response.data["shared_users"], [])


class CategoryListApiTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username= "test",
            password="test",
            email="test@test.com",
            first_name="test"
        )
        self.category1 = Category.objects.create(name="Category1", description="some description", background_url="https://example.com/400", owner=self.user)
        self.category2 = Category.objects.create(name="Category2", description="some description", background_url="https://example.com/400", owner=self.user)
        self.category3 = Category.objects.create(name="Category3", description="some description", background_url="https://example.com/400", owner=self.user)


    def test_get_categories_list(self):

        request = self.factory.get("/api/categories/", format="json")
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"get":"list"})(request)

        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["results"][0]["id"], self.category3.id)
        self.assertEqual(response.data["results"][1]["id"], self.category2.id)
        self.assertEqual(response.data["results"][2]["id"], self.category1.id)

    def test_get_categories_list_limit(self):
        request = self.factory.get(f"/api/categories/?limit=2", format="json")
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"get":"list"})(request)

        self.assertEqual(len(response.data["results"]), 2)

    def test_get_categories_list_offset(self):
        request = self.factory.get(f"/api/categories/?offset=1", format="json")
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"get":"list"})(request)

        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["id"], self.category2.id)
        self.assertEqual(response.data["results"][1]["id"], self.category1.id)

    def test_get_categories_list_filter(self):
        request = self.factory.get(f"/api/categories/?search=1", format="json")
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"get":"list"})(request)

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.category1.id)

    def test_get_categories_list_ordering_created_at(self):
        request = self.factory.get(f"/api/categories/?ordering=created_at", format="json")
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"get":"list"})(request)

        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["results"][0]["id"], self.category1.id)
        self.assertEqual(response.data["results"][1]["id"], self.category2.id)
        self.assertEqual(response.data["results"][2]["id"], self.category3.id)


    def test_get_categories_list_ordering_name(self):
        request = self.factory.get(f"/api/categories/?ordering=name", format="json")
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"get":"list"})(request)

        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["results"][0]["id"], self.category1.id)
        self.assertEqual(response.data["results"][1]["id"], self.category2.id)
        self.assertEqual(response.data["results"][2]["id"], self.category3.id)


