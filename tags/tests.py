from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import User
from tags.models import Tag
from tags.views import TagViewSet

User: User = get_user_model()

class TagsCreateApiTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
                username= "test",
                password="test",
                email="test@test.com",
                first_name="test"
            )


    def test_create_tag(self):
        request_data = {
            "name" : "react",
            "description": "a javascript framework."
        }
        request = self.factory.post("/api/tags/",request_data, format="json")
        force_authenticate(request, self.user)
        response = TagViewSet.as_view({"post":"create"})(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(response.data["name"], request_data["name"])
        self.assertEqual(response.data["description"], request_data["description"])


    def test_name_is_required(self):
        request_data = {
            "description": "a javascript framework."
        }
        request = self.factory.post("/api/tags/",request_data, format="json")
        force_authenticate(request, self.user)
        response = TagViewSet.as_view({"post":"create"})(request)

        self.assertEqual(response.status_code, 400)




class TagListApiTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
                username= "test",
                password="test",
                email="test@test.com",
                first_name="test"
            )

        self.tag1 = Tag.objects.create(name="react", description="a javascript framework")
        self.tag2 = Tag.objects.create(name="django", description="something...")
        self.tag3 = Tag.objects.create(name="python", description="a programming language.")

    def test_get_tag_list(self):
        request = self.factory.get("/api/tags/",format="json")

        force_authenticate(request, user=self.user)
        response = TagViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["results"][0]["id"], self.tag3.id)
        self.assertEqual(response.data["results"][1]["id"], self.tag2.id)
        self.assertEqual(response.data["results"][2]["id"], self.tag1.id)

    def test_tags_filter_by_name(self):
        request = self.factory.get(f"/api/tags/?name=r")
        force_authenticate(request, user=self.user)
        response = TagViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.tag1.id)


    def test_tags_filter_by_ids(self):
        request = self.factory.get(f"/api/tags/?ids={self.tag1.id},{self.tag3.id}&ordering=created_at")
        force_authenticate(request, user=self.user)
        response = TagViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["id"], self.tag1.id)
        self.assertEqual(response.data["results"][1]["id"], self.tag3.id)


class TagDetailAPiTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
                username= "test",
                password="test",
                email="test@test.com",
                first_name="test"
            )

        self.tag1 = Tag.objects.create(name="react", description="a javascript framework")
        self.tag2 = Tag.objects.create(name="django", description="something...")
        self.tag3 = Tag.objects.create(name="python", description="a programming language.")

    def test_get_tag_by_id(self):
        request = self.factory.get(f"/api/tags/{self.tag2.id}", format="json")

        force_authenticate(request, user=self.user)
        response = TagViewSet.as_view({"get":"retrieve"})(request, pk=self.tag2.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.tag2.id)
        self.assertEqual(response.data["name"], self.tag2.name)
        self.assertEqual(response.data["description"], self.tag2.description)


class TagModelTests(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name="react", description="a javascript framework.")

    def test_tag_object_as_string(self):
        self.assertEqual(str(self.tag), f"T{self.tag.id} - {self.tag.name}")
