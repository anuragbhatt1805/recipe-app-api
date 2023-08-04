"""Tests for models"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from decimal import Decimal
from core import models


def create_user(email='samples@example.com',
                username='sample',
                password='testpass123'):
    """Create a sample user"""
    return get_user_model().objects.create_user(
        email=email,
        username=username,
        password=password,
    )


class ModelTests(TestCase):
    """Tests for models"""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = "test@example.com"
        username = "testuser"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            username=username,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        sample_email = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@example.com', 'TEST3@example.com'],
        ]
        for email, excepted in sample_email:
            user = get_user_model().objects.create_user(
                email=email,
                username=email+"user",
                password='testpass123',
            )
            self.assertEqual(user.email, excepted)

    def test_new_user_without_email(self):
        """Test creating user without email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                username="testuser",
                password="testpass123",
            )

    def test_create_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            email="testsuperuser@example.com",
            username="testsuperuser",
            password="testpass123",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.email, "testsuperuser@example.com")

    def test_recipe(self):
        """Test Creating a new recipe is successful"""
        user = get_user_model().objects.create_user(
            email="testUser@example.com",
            username="testUser",
            password="testpass123",
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="test recipe",
            time_minutes=5,
            price=Decimal('5.50'),
            description="test sample description",
        )

        self.assertEqual(str(recipe), recipe.title)
        self.assertEqual(recipe.user, user)

    def test_create_tags(self):
        user = create_user()
        tag = models.Tag.objects.create(
            user=user,
            name="test tag",
        )
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test to create new ingredient"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name="test ingredient1",
        )
        self.assertEqual(str(ingredient), ingredient.name)
