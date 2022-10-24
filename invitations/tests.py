from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import User
from categories.models import AccessLevel, Category
from invitations.models import CategoryInvitation
from invitations.views import (
    CategoryInvitationReceiverViewSet,
    CategoryInvitationSenderViewSet,
)

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

    # TODO

    # def test_create_invitation_when_receiver_exists_in_the_shared_users(self):
    #     self.category.shared_users.add(self.user2)
    #     self.category.save()

    #     request_data = {
    #         "category": self.category.id,
    #         "receiver": self.user2.id,
    #         "note": "I and Test, collaborate to create a better collection.",
    #         "access_level": AccessLevel.READ_WRITE
    #     }

    #     request = self.factory.post("/sender_category_invitations/", request_data, format="json")
    #     force_authenticate(request, user=self.user)

    #     response = CategoryInvitationSenderViewSet.as_view({"post": "create"})(request)

    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(CategoryInvitation.objects.count(), 0)


class InvitationModelTests(TestCase):
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
        self.category = Category.objects.create(name="Category", description="some description", background_url="https://example.com/400",owner=self.user )


    def test_create_an_invitation(self):
        invitation = CategoryInvitation.objects.create(sender=self.user,category=self.category, receiver=self.user2, note="some note", access_level=AccessLevel.READ_ONLY)

        self.assertEqual(CategoryInvitation.objects.count(), 1)

    def test_create_invitation_on_category_of_different_user(self):
        try:
            invitation = CategoryInvitation.objects.create(sender=self.user2,category=self.category, receiver=self.user, note="some note", access_level=AccessLevel.READ_ONLY)
        except ValidationError:
            self.assertEqual(CategoryInvitation.objects.count(), 0)
        else:
            self.fail()


    def test_create_duplicate_invitation(self):
        invitation = CategoryInvitation.objects.create(sender=self.user,category=self.category, receiver=self.user2, note="some note", access_level=AccessLevel.READ_ONLY)

        try:
            invitation2 = CategoryInvitation.objects.create(sender=self.user,category=self.category, receiver=self.user2, note="some note", access_level=AccessLevel.READ_WRITE)
        except ValidationError:
            self.assertEqual(CategoryInvitation.objects.count(), 1)
        else:
            self.fail()

    def test_string_representation_of_category_invitation(self):
        invitation = CategoryInvitation.objects.create(sender=self.user,category=self.category, receiver=self.user2, note="some note", access_level=AccessLevel.READ_ONLY)

        str_repr = f"{invitation.sender} -> {invitation.receiver} for the Category {invitation.category}"
        self.assertEqual(str(invitation), str_repr)

    def test_create_invitation_same_sender_and_receiver(self):
        try:
            invitation = CategoryInvitation.objects.create(sender=self.user,category=self.category, receiver=self.user, note="some note", access_level=AccessLevel.READ_ONLY)
        except ValidationError:
            self.assertEqual(CategoryInvitation.objects.count(), 0)
        else:
            self.fail()


class InvitationListApiTests(TestCase):
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
        self.user3 = User.objects.create_user(
            username= "test3",
            password="test3",
            email="test3@test.com",
            first_name="test3"
        )

        self.category1 = Category.objects.create(name="Category", description="some description", background_url="https://example.com/400",owner=self.user )
        self.category2 = Category.objects.create(name="Category2", description="some description", background_url="https://example.com/400",owner=self.user2 )


        self.invitation1 = CategoryInvitation.objects.create(category=self.category1, sender=self.user, receiver=self.user2, note="some note", access_level=AccessLevel.READ_WRITE)
        self.invitation2 = CategoryInvitation.objects.create(category=self.category1, sender=self.user, receiver=self.user3, note="some note", access_level=AccessLevel.READ_WRITE)

        self.invitation3 = CategoryInvitation.objects.create(category=self.category2, sender=self.user2, receiver=self.user3, note="some note", access_level=AccessLevel.READ_WRITE)


    def test_get_sent_invitations(self):
        request = self.factory.get(f"/sender_category_invitations/", format="json")
        force_authenticate(request,user=self.user)

        response = CategoryInvitationSenderViewSet.as_view({"get":"list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["id"], self.invitation1.id )
        self.assertEqual(response.data["results"][1]["id"], self.invitation2.id )


    def test_get_received_invitation(self):
        request = self.factory.get(f"/receiver_category_invitations/", format="json")
        force_authenticate(request,user=self.user)

        response = CategoryInvitationReceiverViewSet.as_view({"get":"list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

        request = self.factory.get(f"/receiver_category_invitations/", format="json")
        force_authenticate(request,user=self.user2)

        response = CategoryInvitationReceiverViewSet.as_view({"get":"list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.invitation1.id)

class InvitationDetailApiTests(TestCase):
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
        self.user3 = User.objects.create_user(
            username= "test3",
            password="test3",
            email="test3@test.com",
            first_name="test3"
        )

        self.category1 = Category.objects.create(name="Category", description="some description", background_url="https://example.com/400",owner=self.user )
        self.category2 = Category.objects.create(name="Category2", description="some description", background_url="https://example.com/400",owner=self.user2 )


        self.invitation1 = CategoryInvitation.objects.create(category=self.category1, sender=self.user, receiver=self.user2, note="some note", access_level=AccessLevel.READ_WRITE)
        self.invitation2 = CategoryInvitation.objects.create(category=self.category1, sender=self.user, receiver=self.user3, note="some note", access_level=AccessLevel.READ_WRITE)

        self.invitation3 = CategoryInvitation.objects.create(category=self.category2, sender=self.user2, receiver=self.user3, note="some note", access_level=AccessLevel.READ_WRITE)


    def test_get_sent_invitation(self):
        request = self.factory.get(f"/sender_category_invitations/{self.invitation1.id}", format="json")
        force_authenticate(request,user=self.user)
        response = CategoryInvitationSenderViewSet.as_view({"get":"retrieve"})(request, pk=self.invitation1.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.invitation1.id)
        self.assertEqual(response.data["category"], self.invitation1.category.id )
        self.assertEqual(response.data["category_description"], self.invitation1.category.description )
        self.assertEqual(response.data["category_background_url"], self.invitation1.category.background_url )
        self.assertEqual(response.data["sender"], self.user.id )
        self.assertEqual(response.data["sender_username"], self.user.username )
        self.assertEqual(response.data["sender_avatar"], self.user.avatar )
        self.assertEqual(response.data["receiver"], self.invitation1.receiver.id )
        self.assertEqual(response.data["receiver_username"], self.invitation1.receiver.username )
        self.assertEqual(response.data["receiver_avatar"], self.invitation1.receiver.avatar )
        self.assertEqual(response.data["note"], self.invitation1.note )
        self.assertEqual(response.data["access_level"], self.invitation1.access_level )


    def test_get_sent_invitation_sent_by_different_user(self):
        request = self.factory.get(f"/sender_category_invitations/{self.invitation3.id}", format="json")
        force_authenticate(request,user=self.user)
        response = CategoryInvitationSenderViewSet.as_view({"get":"retrieve"})(request, pk=self.invitation3.id)

        self.assertEqual(response.status_code, 404)

    def test_get_received_invitation(self):
        request = self.factory.get(f"/receiver_category_invitations/{self.invitation1.id}", format="json")
        force_authenticate(request, user=self.user2)
        response = CategoryInvitationReceiverViewSet.as_view({"get":"retrieve"})(request, pk= self.invitation1.id)

        self.assertEqual(response.status_code, 200)

    def test_get_received_invitation_of_different_user(self):
        request = self.factory.get(f"/sender_category_invitations/{self.invitation2.id}", format="json")
        force_authenticate(request,user=self.user2)
        response = CategoryInvitationReceiverViewSet.as_view({"get":"retrieve"})(request, pk=self.invitation2.id)

        self.assertEqual(response.status_code, 404)

    def test_delete_when_invitation_is_accepted_is_none(self):
        total_invitations = CategoryInvitation.objects.count()
        request = self.factory.delete(f"/sender_category_invitations/{self.invitation1.id}", format="json")
        force_authenticate(request, user=self.user)

        response = CategoryInvitationSenderViewSet.as_view({"delete": "destroy"})(request, pk=self.invitation1.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(CategoryInvitation.objects.count(), total_invitations-1)

    def test_delete_when_invitation_is_accepted_is_not_none(self):
        total_invitations = CategoryInvitation.objects.count()
        self.invitation1.is_accepted = True
        self.invitation1.save()
        request = self.factory.delete(f"/sender_category_invitations/{self.invitation1.id}", format="json")
        force_authenticate(request, user=self.user)

        response = CategoryInvitationSenderViewSet.as_view({"delete": "destroy"})(request, pk=self.invitation1.id)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CategoryInvitation.objects.count(), total_invitations)


    # TODO : test_cases for accept and decline requests
