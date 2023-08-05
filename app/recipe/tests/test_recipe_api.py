"""
Test for recipe APIs.
"""
from decimal import Decimal
# import tempfile
# import os
# from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def image_upload_url(recipe_id):
    """Create and Return url for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'description': 'Sample description',
        'price': Decimal('5.00'),
        'time_minutes': 10,
        'link': 'https://sample.com/example',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe APIs"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe APIs"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            username='user',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            username='user2',
            password='password123',
        )
        create_recipe(user=user2)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test retrieving recipe detail"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)

        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test Creating a Recipie"""
        payload = {
            'title': 'Chocolate cheesecake',
            'description': 'Chocolate cheesecake description',
            'price': Decimal('5.99'),
            'time_minutes': 30,
            'link': 'https://sample.com/recipe',
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(recipe.user, self.user)

    def test_create_recipe_with_tag(self):
        """Creating Recipe with new tags"""
        payload = {
            'title': 'Chocolate cheesecake',
            'description': 'Chocolate cheesecake description',
            'price': Decimal('5.99'),
            'time_minutes': 30,
            'link': 'https://sample.com/recipe',
            'tags': [{'name': 'Vegan'}, {'name': 'Dessert'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipies = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipies.count(), 1)
        recipe = recipies[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_existing_tag(self):
        """Creating Recipe with existing Tag"""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Chocolate cheesecake',
            'description': 'Chocolate cheesecake description',
            'price': Decimal('5.99'),
            'time_minutes': 30,
            'link': 'https://sample.com/recipe',
            'tags': [{'name': 'Vegan'}, {'name': 'Indian'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_updating_recipe(self):
        """Creating new tags on Updating  the Recipe"""
        recipe = create_recipe(user=self.user)
        payload = {
            'tags': [{
                'name': 'Vegan',
            }]
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Vegan')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assiging an existing tag when updating Recipe"""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lucent = Tag.objects.create(user=self.user, name='lucent')
        payload = {
            'tags': [{
                'name': 'lucent',
            }]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lucent, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Clearing Recipe Tags"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_new_recipe_with_new_ingredient(self):
        """Create Recipes with new Ingredients"""
        payload = {
            "title": "Thai prawn red curry",
            "description": "A quick and easy Thai curry with prawns",
            "price": Decimal('5.99'),
            "time_minutes": 20,
            "link": "https://sample.com/recipe",
            "ingredients": [
                {"name": "Prawns", },
                {"name": "Red curry paste", },
            ],
            "tags": [
                {"name": "Thai", },
            ],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.filter(user=self.user)

        self.assertEqual(recipe.count(), 1)
        recipe = recipe[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_new_recipe_existing_ingredient(self):
        """Create Recipes with existing Ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name='Prawns')

        payload = {
            "title": "Thai prawn red curry",
            "description": "A quick and easy Thai curry with prawns",
            "price": Decimal('5.99'),
            "time_minutes": 20,
            "link": "https://sample.com/recipe",
            "ingredients": [
                {"name": "Prawns", },
                {"name": "Red curry paste", },
            ],
            "tags": [
                {"name": "Thai", },
            ],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.filter(user=self.user)

        self.assertEqual(recipe.count(), 1)
        recipe = recipe[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_update(self):
        """Test Creating an Ingredient when updating a recipe"""

        recipe = create_recipe(user=self.user)

        payload = {
            "ingredients": [
                {"name": "Prawns", },
            ],
            "tags": [
                {"name": "Thai", },
            ],
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_Ingredient = Ingredient.objects.get(
            user=self.user, name='Prawns')
        self.assertIn(new_Ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an exsisting Ingredient to recipe"""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Prawns')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(user=self.user, name='Chilli')
        payload = {
            "ingredients": [
                {"name": "Chilli", },
            ],
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test to remove recipe ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name='Prawns')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {
            "ingredients": [],
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """Test Filtering by tags"""
        r1 = create_recipe(user=self.user, title='Thai vegetable curry')
        r2 = create_recipe(user=self.user, title='Aubergine with tahini')
        tag1 = Tag.objects.create(user=self.user, name='Vegan')
        tag2 = Tag.objects.create(user=self.user, name='Vegetarian')
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_recipe(user=self.user, title='Fish and chips')

        params = {
            'tags': f'{tag1.id},{tag2.id}',
        }
        res = self.client.get(RECIPE_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_by_ingredients(self):
        """Test Filtering by ingredients"""
        r1 = create_recipe(user=self.user, title='Posh beans on toast')
        r2 = create_recipe(user=self.user, title='Chicken cacciatore')
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Feta cheese'
        )
        ingredient2 = Ingredient.objects.create(user=self.user, name='Chicken')
        r1.ingredients.add(ingredient1)
        r2.ingredients.add(ingredient2)
        r3 = create_recipe(user=self.user, title='Steak and mushrooms')

        params = {
            'ingredients': f'{ingredient1.id},{ingredient2.id}',
        }
        res = self.client.get(RECIPE_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)


class ImageUploadTestCase(TestCase):
    """Test Image Upload"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='samples',
            email='samples@example.com',
            password='samples123',
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    # def test_upload_image(self):
    #     """Test for Uploading the file"""
    #     url = image_upload_url(self.recipe.id)
    #     with tempfile.NamedTemporaryFile(suffix='.jpg') as img_file:
    #         image = Image.new('RGB', (10, 10))
    #         image.save(img_file, format='JPEG')
    #         img_file.seek(0)

    #         res = self.client.post(
    #             url,
    #             {'image': img_file},
    #             format='multipart',
    #         )
    #     self.recipe.refresh_from_db()
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertIn('image', res.data)
    #     self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_bad_request(self):
        """Test Uploading invalid image"""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'NotImage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
