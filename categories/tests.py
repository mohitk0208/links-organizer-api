import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import User
from categories.models import AccessLevel, Category, CategoryAccess
from categories.views import CategoryAccessViewSet, CategoryViewSet

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
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(response.data["name"], request_data["name"])
        self.assertEqual(response.data["description"], request_data["description"])
        self.assertEqual(response.data["background_url"], request_data["background_url"])
        self.assertEqual(response.data["owner"], self.user.id)
        self.assertEqual(response.data["owner_username"], self.user.username)
        self.assertEqual(response.data["owner_avatar"], self.user.avatar)
        self.assertEqual(response.data["shared_users"], [])

    def test_same_category_name_same_owner(self):
        request_data = {
            "name": "category1",
            "description": "This is a test category.",
            "background_url": "https://picsum.photos/400"
        }
        category1 = Category.objects.create(name=request_data["name"], description=request_data["description"], background_url=request_data["background_url"], owner=self.user)

        request = self.factory.post("/api/categories/",request_data,format="json")
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"post": "create"})(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["name"][0], "Category already exists")

    def test_same_category_name_different_owner(self):
        request_data = {
            "name": "category1",
            "description": "This is a test category.",
            "background_url": "https://picsum.photos/400"
        }
        user2 = User.objects.create_user(
            username= "test2",
            password="test2",
            email="test2@test.com",
            first_name="test2"
        )

        category1 = Category.objects.create(name=request_data["name"], description=request_data["description"], background_url=request_data["background_url"], owner=user2)

        request = self.factory.post("/api/categories/",request_data,format="json")
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

class CategoryDetailApiTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
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


    def test_get_category_detail(self):
        request = self.factory.get(f"/api/categories/{self.category1.id}/", format="json")
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"get":"retrieve"})(request, pk=self.category1.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.category1.name)
        self.assertEqual(response.data["description"], self.category1.description)
        self.assertEqual(response.data["background_url"], self.category1.background_url)
        self.assertEqual(response.data["owner"], self.category1.owner.id)
        self.assertEqual(response.data["owner_username"], self.category1.owner.username)
        self.assertEqual(response.data["owner_avatar"], self.category1.owner.avatar)
        self.assertEqual(response.data["shared_users"], [])

    def test_get_category_of_different_user(self):
        user2 = User.objects.create_user(
            username= "test2",
            password="test2",
            email="test2@test.com",
            first_name="test2"
        )
        category4 = Category.objects.create(name="Category3", description="some description", background_url="https://example.com/400", owner=user2)

        request = self.factory.get(f"/api/categories/{category4.id}/", format="json")
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"get":"retrieve"})(request, pk=category4.id)

        self.assertEqual(response.status_code, 404)

    def test_update_category(self):
        updated_data = {
            "name": "new_name",
            "description": "This is updated description."
        }
        request = self.factory.put(f"/api/categories/{self.category1.id}/", updated_data,format="json")
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"put":"update"})(request, pk=self.category1.id)

        self.category1 = Category.objects.get(id=self.category1.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.category1.name, updated_data["name"])
        self.assertEqual(response.data["name"], self.category1.name)
        self.assertEqual(self.category1.description, updated_data["description"])
        self.assertEqual(response.data["description"], self.category1.description)
        self.assertEqual(response.data["background_url"], self.category1.background_url)
        self.assertEqual(response.data["owner"], self.category1.owner.id)
        self.assertEqual(response.data["owner_username"], self.category1.owner.username)
        self.assertEqual(response.data["owner_avatar"], self.category1.owner.avatar)
        self.assertEqual(response.data["shared_users"], [])

    def test_partial_update_category(self):
        updated_data = {
            "description": "This is updated description."
        }
        request = self.factory.patch(f"/api/categories/{self.category1.id}/", updated_data,format="json")
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"patch":"partial_update"})(request, pk=self.category1.id)

        self.category1 = Category.objects.get(id=self.category1.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.category1.description, updated_data["description"])
        self.assertEqual(response.data["description"], self.category1.description)
        self.assertEqual(response.data["name"], self.category1.name)
        self.assertEqual(response.data["background_url"], self.category1.background_url)
        self.assertEqual(response.data["owner"], self.category1.owner.id)
        self.assertEqual(response.data["owner_username"], self.category1.owner.username)
        self.assertEqual(response.data["owner_avatar"], self.category1.owner.avatar)
        self.assertEqual(response.data["shared_users"], [])

    def test_make_category_as_parent_of_itself(self):
        updated_data = {
            "parent_category": self.category1.id
        }
        request = self.factory.patch(f"/api/categories/{self.category1.id}/", updated_data,format="json")
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"patch":"partial_update"})(request, pk=self.category1.id)

        self.category1 = Category.objects.get(id=self.category1.id)

        self.assertEqual(response.status_code, 400)


    def test_delete_category(self):
        request = self.factory.delete(f"/api/categories/{self.category1.id}/", format="json")
        force_authenticate(request, user=self.user)
        response = CategoryViewSet.as_view({"delete":"destroy"})(request, pk=self.category1.id)

        self.assertEqual(response.status_code, 204)
        try:
            self.category1 = Category.objects.get(id=self.category1.id)
        except Category.DoesNotExist:
            self.category1 = None

        self.assertEqual(self.category1, None)

class CategoryModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username= "test",
            password="test",
            email="test@test.com",
            first_name="test"
        )
        self.category1 = Category.objects.create(name="Category1", description="some description", background_url="https://example.com/400", owner=self.user)

    def test_string_representation_of_category(self):
        self.assertEqual(str(self.category1), self.category1.name)

    def test_get_category_function(self):
        self.assertEqual(self.category1, self.category1.get_category())

    def test_parent_category_is_itself(self):
        self.category2 = Category.objects.create(name="Category2", description="snkjd", background_url="https://exampleimage.com/400", owner=self.user)
        try:
            self.category2.parent_category = self.category2
            self.category2.save()
        except:
            pass
        else:
            self.fail()


class CategoryAccessApiTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user1 = User.objects.create_user(
            username= "test",
            password="test",
            email="test@test.com",
            first_name="test"
        )
        self.user2 = User.objects.create_user(
            username= "test2",
            password="test2",
            email="test2@test.com",
            first_name="test2"
        )
        self.category1 = Category.objects.create(name="Category1", description="some description", background_url="https://example.com/400", owner=self.user1)
        self.category2 = Category.objects.create(name="Category2", description="snkjd", background_url="https://exampleimage.com/400", owner=self.user1)

        self.category_access = CategoryAccess.objects.create(user=self.user2, category=self.category1, level=AccessLevel.READ_ONLY)



    def test_update_access_level(self):
        request_data = {
            "level": AccessLevel.READ_WRITE
        }
        request = self.factory.patch(f"/api/category_access/{self.category_access.id}/", request_data, format="json")

        force_authenticate(request, user=self.user1)
        response = CategoryAccessViewSet.as_view({"patch":"partial_update"})(request, pk=self.category_access.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["level"], AccessLevel.READ_WRITE)

    def test_update_access_level_with_wrong_user(self):
        request_data = {
            "level": AccessLevel.READ_WRITE
        }
        request = self.factory.patch(f"/api/category_access/{self.category_access.id}/", request_data, format="json")

        force_authenticate(request, user=self.user2)
        response = CategoryAccessViewSet.as_view({"patch":"partial_update"})(request, pk=self.category_access.id)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(CategoryAccess.objects.get(id=self.category_access.id).level, AccessLevel.READ_ONLY)


    def test_remove_user_from_the_shared_category(self):
        self.assertEqual(len(self.category1.shared_users.all()), 1)

        request = self.factory.delete(f"/api/category_access/{self.category_access.id}/", format="json")
        force_authenticate(request, user=self.user1)

        response = CategoryAccessViewSet.as_view({"delete":"destroy"})(request, pk=self.category_access.id)


        self.assertEqual(response.status_code, 204)
        self.assertEqual(CategoryAccess.objects.count(), 0)
        self.assertEqual(len(self.category1.shared_users.all()), 0)


    def test_remove_user_from_the_shared_category_with_wrong_user(self):
        self.assertEqual(len(self.category1.shared_users.all()), 1)

        request = self.factory.delete(f"/api/category_access/{self.category_access.id}/", format="json")
        force_authenticate(request, user=self.user2)

        response = CategoryAccessViewSet.as_view({"delete":"destroy"})(request, pk=self.category_access.id)


        self.assertEqual(response.status_code, 403)
        self.assertEqual(CategoryAccess.objects.count(), 1)
        self.assertEqual(len(self.category1.shared_users.all()), 1)



