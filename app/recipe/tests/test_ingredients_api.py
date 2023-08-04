"""Test for the Ingredient API"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Return the detail URL for a given ingredient"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email="samples@example.com",
                username="sample",
                password="password"):
    """create and return user"""
    return get_user_model().objects.create_user(
        email=email,
        username=username,
        password=password,
    )


class PublicIngredientApiTests(TestCase):
    """Test the publicly available Ingredient API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving ingredients"""
        response = self.client.get(INGREDIENT_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test the Authenticated API Test"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Salt")

        response = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_user(self):
        """Test that ingredients for the authenticated user are returned"""
        user2 = create_user(
            email="test@example.com",
            username="test",
            password="password",
        )
        Ingredient.objects.create(user=user2, name="Vinegar")
        ingredient = Ingredient.objects.create(
            user=self.user,
            name="Tumeric"
        )

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(
            res.data[0]['name'],
            ingredient.name,
        )
        self.assertEqual(
            res.data[0]['id'],
            ingredient.id,
        )

    def test_Update_ingredient(self):
        """Test updating an ingredient"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name="Tumeric",
        )
        payload = {
            'name': 'Cabbage',
        }
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        ingredient.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test Deleting an ingredient"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name="Tumeric",
        )
        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredient = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredient.exists())
