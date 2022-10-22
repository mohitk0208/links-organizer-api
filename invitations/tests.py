from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import User
from categories.models import AccessLevel, Category
from invitations.models import CategoryInvitation
from invitations.views import CategoryInvitationSenderViewSet

User: User = get_user_model()


class InvitationCreateApiTests(TestCase):
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
        self.category = Category.objects.create(name="Category", description="some description", background_url="https://example.com/400",owner=self.user )


    def test_create_a_invitation(self):
        request_data = {
            "category": self.category.id,
            "receiver": self.user2.id,
            "note": "I and Test, collaborate to create a better collection.",
            "access_level": AccessLevel.READ_WRITE
        }

        request = self.factory.post("/sender_category_invitations/", request_data, format="json")
        force_authenticate(request, user=self.user)

        response = CategoryInvitationSenderViewSet.as_view({"post": "create"})(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(CategoryInvitation.objects.count(), 1)
        self.assertEqual(response.data["category"], self.category.id )
        self.assertEqual(response.data["category_description"], self.category.description )
        self.assertEqual(response.data["category_background_url"], self.category.background_url )
        self.assertEqual(response.data["sender"], self.user.id )
        self.assertEqual(response.data["sender_username"], self.user.username )
        self.assertEqual(response.data["sender_avatar"], self.user.avatar )
        self.assertEqual(response.data["receiver"], self.user2.id )
        self.assertEqual(response.data["receiver_avatar"], self.user2.avatar )
        self.assertEqual(response.data["receiver_avatar"], self.user2.avatar )
        self.assertEqual(response.data["note"], request_data["note"] )
        self.assertEqual(response.data["access_level"], request_data["access_level"] )
        self.assertEqual(response.data["is_accepted"], None)


    def test_create_a_invitation_with_same_sender_and_receiver(self):
        request_data = {
            "category": self.category.id,
            "receiver": self.user.id,
            "note": "I and Test, collaborate to create a better collection.",
            "access_level": AccessLevel.READ_WRITE
        }

        request = self.factory.post("/sender_category_invitations/", request_data, format="json")
        force_authenticate(request, user=self.user)

        response = CategoryInvitationSenderViewSet.as_view({"post": "create"})(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CategoryInvitation.objects.count(), 0)


    def test_create_duplicate_invitation(self):
        invitation = CategoryInvitation.objects.create(category=self.category,sender=self.user, receiver=self.user2, note="I am Test, collaborate to create a better collection.", access_level=AccessLevel.READ_WRITE)

        request_data = {
            "category": invitation.category.id,
            "receiver": invitation.receiver.id,
            "note": invitation.note,
            "access_level": invitation.access_level
        }

        request = self.factory.post("/sender_category_invitations/", request_data, format="json")
        force_authenticate(request, user=self.user)

        response = CategoryInvitationSenderViewSet.as_view({"post": "create"})(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CategoryInvitation.objects.count(), 1)

    def test_create_invitation_of_non_owned_category(self):
        request_data = {
            "category": self.category.id,
            "receiver": self.user.id,
            "note": "I and Test, collaborate to create a better collection.",
            "access_level": AccessLevel.READ_WRITE
        }

        request = self.factory.post("/sender_category_invitations/", request_data, format="json")
        force_authenticate(request, user=self.user2)

        response = CategoryInvitationSenderViewSet.as_view({"post": "create"})(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CategoryInvitation.objects.count(), 0)

    def test_create_invitation_receiver_does_not_exist(self):
        request_data = {
            "category": self.category.id,
            "receiver": 243,
            "note": "I and Test, collaborate to create a better collection.",
            "access_level": AccessLevel.READ_WRITE
        }

        request = self.factory.post("/sender_category_invitations/", request_data, format="json")
        force_authenticate(request, user=self.user)

        response = CategoryInvitationSenderViewSet.as_view({"post": "create"})(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CategoryInvitation.objects.count(), 0)
