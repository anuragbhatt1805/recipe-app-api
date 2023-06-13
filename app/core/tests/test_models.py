"""Tests for models"""
from django.test import TestCase
from django.contrib.auth import get_user_model


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
