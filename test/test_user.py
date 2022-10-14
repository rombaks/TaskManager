import factory
from http import HTTPStatus
from typing import List, Union

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from task_manager.main.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("word")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    date_of_birth = "1962-09-23"
    phone = factory.Faker("phone_number")


class TestViewSetBase(APITestCase):
    user: User = None
    client: APIClient = None
    basename: str

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = cls.create_api_user()
        cls.client = APIClient()

    @staticmethod
    def create_api_user():
        user_attributes = factory.build(dict, FACTORY_CLASS=UserFactory)
        return User.objects.create(**user_attributes)

    @classmethod
    def detail_url(cls, key: Union[int, str]) -> str:
        return reverse(f"{cls.basename}-detail", args=[key])

    @classmethod
    def list_url(cls, args: List[Union[str, int]] = None) -> str:
        return reverse(f"{cls.basename}-list", args=args)

    def create(self, data: dict, args: List[Union[str, int]] = None) -> dict:
        self.client.force_login(self.user)
        response = self.client.post(self.list_url(args), data=data)
        assert response.status_code == HTTPStatus.CREATED, response.content
        return response.data

    def retrieve(self, id: int = None) -> dict:
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url(id))
        assert response.status_code == HTTPStatus.OK, response.content
        return response.data

    def update(self, data: dict, id: int = None) -> dict:
        self.client.force_login(self.user)
        response = self.client.patch(self.detail_url(id), data=data)
        assert response.status_code == HTTPStatus.OK, response.content
        return response.data

    def delete(self, id: int = None) -> dict:
        self.client.force_login(self.user)
        response = self.client.delete(self.detail_url(id))
        assert response.status_code == HTTPStatus.NO_CONTENT
        return response


class TestUserViewSet(TestViewSetBase):
    basename = "users"
    user_attributes = factory.build(dict, FACTORY_CLASS=UserFactory)

    @staticmethod
    def expected_details(entity: dict, attributes: dict):
        return {**attributes, "id": entity["id"]}

    def test_create(self):
        user = self.create(self.user_attributes)
        expected_response = self.expected_details(user, self.user_attributes)
        assert user == expected_response

    def test_retrieve(self):
        user = self.create(self.user_attributes)
        id = self.expected_details(user, self.user_attributes)["id"]
        expected_response = self.retrieve(id=id)
        assert user == expected_response

    def test_update(self):
        user = self.create(self.user_attributes)
        id = self.expected_details(user, self.user_attributes)["id"]
        new_data = {"last_name": "Smith"}
        expected_response = self.update(data=new_data, id=id)
        updated_user = self.retrieve(id=id)
        assert updated_user == expected_response

    def test_delete(self):
        user = self.create(self.user_attributes)
        id = self.expected_details(user, self.user_attributes)["id"]
        expected_response = self.delete(id=id)
        assert expected_response.status_code == HTTPStatus.NO_CONTENT

    def test_not_found(self):
        expected_response = self.client.get("/not_found")
        assert expected_response.status_code == HTTPStatus.NOT_FOUND
