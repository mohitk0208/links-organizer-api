from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import User
from categories.models import Category
from links.models import Link
from links.views import LinksViewSet
from tags.models import Tag

User: User = get_user_model()


class LinkCreateApiTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
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

        self.category1 = Category.objects.create(name="Category1", description="some description", background_url="https://example.com/400", owner=self.user)
        self.category2 = Category.objects.create(name="Category2", description="some description", background_url="https://example.com/400", owner=self.user)

        self.category3 = Category.objects.create(name="Category3_user2", description="some description", background_url="https://example.com/400", owner=self.user2)


        self.tag1 = Tag.objects.create(name="react", description="a javascript framework")
        self.tag2 = Tag.objects.create(name="django", description="something...")
        self.tag3 = Tag.objects.create(name="python", description="a programming language.")


    def test_create_link(self):
        request_data = {
            "url": "https://example.com",
            "category": self.category1.id,
            "description": "This is some description...",
            "tags": [self.tag1.id, self.tag2.id]
        }
        request = self.factory.post("/api/links/", request_data, format="json")

        force_authenticate(request, user=self.user)
        response = LinksViewSet.as_view({"post": "create"})(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["url"], request_data["url"])
        self.assertEqual(response.data["category"], request_data["category"])
        self.assertEqual(response.data["description"], request_data["description"])
        self.assertEqual(response.data["owner"], self.user.id)
        self.assertEqual(response.data["owner_username"], self.user.username)
        self.assertEqual(response.data["owner_avatar"], self.user.avatar)
        self.assertEqual(response.data["category_background_url"], self.category1.background_url)

        request_tags = [
            OrderedDict(id=self.tag1.id, name=self.tag1.name),
            OrderedDict(id=self.tag2.id, name=self.tag2.name)
        ]

        self.assertEqual(len(response.data["tags"]), len(request_tags))
        self.assertTrue(response.data["tags"][0] in request_tags)
        self.assertTrue(response.data["tags"][1] in request_tags)


    def test_duplicate_link_in_same_category(self):
        request_data = {
            "url": "https://example.com",
            "category": self.category1.id,
            "description": "This is some description...",
            "tags": [self.tag1.id, self.tag2.id]
        }
        new_link1 = Link.objects.create(url=request_data["url"], category=self.category1, owner=self.user)

        request = self.factory.post("/api/links/", request_data, format="json")

        force_authenticate(request, user=self.user)
        response = LinksViewSet.as_view({"post": "create"})(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["url"][0], "This URL is already in use.")


    def test_duplicate_link_in_different_category(self):
        request_data = {
            "url": "https://example.com",
            "category": self.category1.id,
            "description": "This is some description...",
            "tags": [self.tag1.id, self.tag2.id]
        }
        new_link1 = Link.objects.create(url=request_data["url"], category=self.category2, owner=self.user)

        request = self.factory.post("/api/links/", request_data, format="json")

        force_authenticate(request, user=self.user)
        response = LinksViewSet.as_view({"post": "create"})(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["url"][0], "This URL is already in use.")


    def test_duplicate_link_but_different_user(self):
        request_data = {
            "url": "https://example.com",
            "category": self.category1.id,
            "description": "This is some description...",
            "tags": [self.tag1.id, self.tag2.id]
        }
        new_link1 = Link.objects.create(url=request_data["url"], category=self.category3, owner=self.user2)

        request = self.factory.post("/api/links/", request_data, format="json")

        force_authenticate(request, user=self.user)
        response = LinksViewSet.as_view({"post": "create"})(request)

        self.assertEqual(response.status_code, 201)


    def test_create_link_different_category_owner(self):
        request_data = {
            "url": "https://example1.com",
            "category": self.category3.id,
            "description": "This is some description...",
            "tags": [self.tag1.id, self.tag2.id]
        }

        request = self.factory.post("/api/links/", request_data, format="json")

        force_authenticate(request, user=self.user)
        response = LinksViewSet.as_view({"post": "create"})(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["category"][0], "Category does not exist.")


    def test_create_link_when_category_does_not_exist(self):
        request_data = {
            "url": "https://example1.com",
            "category": 10001,
            "description": "This is some description...",
            "tags": [self.tag1.id, self.tag2.id]
        }

        request = self.factory.post("/api/links/", request_data, format="json")

        force_authenticate(request, user=self.user)
        response = LinksViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, 400)


class LinkListApiTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
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

        self.category1 = Category.objects.create(name="Category1", description="some description", background_url="https://example.com/400", owner=self.user)
        self.category2 = Category.objects.create(name="Category2", description="some description", background_url="https://example.com/400", owner=self.user)

        self.category3 = Category.objects.create(name="Category3_user2", description="some description", background_url="https://example.com/400", owner=self.user2)


        self.tag1 = Tag.objects.create(name="react", description="a javascript framework")
        self.tag2 = Tag.objects.create(name="django", description="something...")
        self.tag3 = Tag.objects.create(name="python", description="a programming language.")

        self.link1 = Link.objects.create(url="https://example1.com", description="link1 description", category=self.category1, owner=self.user)
        self.link1.tags.add(self.tag1)
        self.link1.tags.add(self.tag2)

        self.link2 = Link.objects.create(url="https://example2.com", description="link2 description 2", category=self.category1, owner=self.user)
        self.link2.tags.add(self.tag3)
        self.link2.tags.add(self.tag2)

        self.link3 = Link.objects.create(url="https://example3.com", description="link3 description 3", category=self.category3, owner=self.user2)
        self.link3.tags.add(self.tag3)


    def test_get_links(self):
        request = self.factory.get("/api/links/", format="json")
        force_authenticate(request, self.user)

        response = LinksViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["id"], self.link2.id)
        self.assertEqual(response.data["results"][1]["id"], self.link1.id)


    def test_get_links_by_limit(self):
        request = self.factory.get("/api/links/?limit=1", format="json")
        force_authenticate(request, self.user)

        response = LinksViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.link2.id)


    def test_get_links_by_offset(self):
        request = self.factory.get("/api/links/?offset=1", format="json")
        force_authenticate(request, self.user)

        response = LinksViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.link1.id)


    def test_get_links_ordering_created_at(self):
        request = self.factory.get("/api/links/?ordering=created_at", format="json")
        force_authenticate(request, self.user)

        response = LinksViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["id"], self.link1.id)
        self.assertEqual(response.data["results"][1]["id"], self.link2.id)


    def test_get_links_filter_search(self):
        request = self.factory.get("/api/links/?search=1", format="json")
        force_authenticate(request, self.user)

        response = LinksViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.link1.id)


    def test_get_links_filter_by_tags(self):
        request = self.factory.get(f"/api/links/?tags={self.tag2.id}, {self.tag3.id}", format="json")
        force_authenticate(request, self.user)

        response = LinksViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.link2.id)



class LinkDetailApiTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
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

        self.category1 = Category.objects.create(name="Category1", description="some description", background_url="https://example.com/400", owner=self.user)
        self.category2 = Category.objects.create(name="Category2", description="some description", background_url="https://example.com/400", owner=self.user)


        self.tag1 = Tag.objects.create(name="react", description="a javascript framework")
        self.tag2 = Tag.objects.create(name="django", description="something...")
        self.tag3 = Tag.objects.create(name="python", description="a programming language.")

        self.link = Link.objects.create(url="https://example1.com", description="link1 description", category=self.category1, owner=self.user)
        self.link.tags.add(self.tag1)
        self.link.tags.add(self.tag2)


    def test_get_link_detail(self):
        request = self.factory.get(f"/api/links/{self.link.id}", format="json")
        force_authenticate(request, user=self.user)

        response = LinksViewSet.as_view({"get": "retrieve"})(request, pk=self.link.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.link.id)
        self.assertEqual(response.data["url"], self.link.url)
        self.assertEqual(response.data["category"], self.link.category.id)
        self.assertEqual(response.data["description"], self.link.description)
        self.assertEqual(response.data["owner"], self.user.id)
        self.assertEqual(response.data["owner_username"], self.user.username)
        self.assertEqual(response.data["owner_avatar"], self.user.avatar)
        self.assertEqual(response.data["category_background_url"], self.category1.background_url)

        request_tags = [
            OrderedDict(id=self.tag1.id, name=self.tag1.name),
            OrderedDict(id=self.tag2.id, name=self.tag2.name)
        ]

        self.assertEqual(len(response.data["tags"]), len(request_tags))
        self.assertTrue(response.data["tags"][0] in request_tags)
        self.assertTrue(response.data["tags"][1] in request_tags)

    def test_get_link_detail_of_different_user(self):
        request = self.factory.get(f"/api/links/{self.link.id}", format="json")
        force_authenticate(request, user=self.user2)

        response = LinksViewSet.as_view({"get": "retrieve"})(request, pk=self.link.id)

        self.assertEqual(response.status_code, 404)


    def test_delete_link(self):
        request = self.factory.delete(f"/api/links/{self.link.id}", format="json")
        force_authenticate(request, user=self.user)

        response = LinksViewSet.as_view({"delete": "destroy"})(request, pk=self.link.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Link.objects.count(), 0)


    def test_partial_update_link(self):
        updated_data = {
            "url" :"https://newexample1.com",
            "description": "changed",
            "category": self.category2.id
        }
        request = self.factory.patch(f"/api/links/{self.link.id}", updated_data,format="json")
        force_authenticate(request, user=self.user)

        response = LinksViewSet.as_view({"patch":"partial_update"})(request, pk=self.link.id)
        self.link = Link.objects.get(id=self.link.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["url"], updated_data["url"])
        self.assertEqual(self.link.url, updated_data["url"])
        self.assertEqual(response.data["description"], updated_data["description"])
        self.assertEqual(self.link.description, updated_data["description"])
        self.assertEqual(response.data["category"], updated_data["category"])
        self.assertEqual(self.link.category.id, updated_data["category"])




class LinkModelTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
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

        self.category1 = Category.objects.create(name="Category1", description="some description", background_url="https://example.com/400", owner=self.user)

        self.category2 = Category.objects.create(name="Category2", description="some description", background_url="https://example.com/400", owner=self.user2)
        self.tag1 = Tag.objects.create(name="react", description="a javascript framework")

        self.link = Link.objects.create(url="https://linkexample.com", description="somec", owner=self.user, category=self.category1)
        self.link.tags.add(self.tag1)

    def test_create_link_in_category_of_different_user(self):
        try:
            link = Link.objects.create(url="https://linkexampleds.com", description="somec", owner=self.user, category=self.category2)
            self.assertTrue(False)
        except ValidationError as e:
            self.assertTrue(True)


    def test_get_category_function(self):
        c = self.link.get_category()

        self.assertEqual(c , self.category1)


    def test_string_representation_of_link(self):
        self.assertEqual(str(self.link), self.link.url)

