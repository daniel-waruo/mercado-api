from django.test import TestCase
from ..models import Category


class TestGetByPosition(TestCase):
    def setUp(self) -> None:
        Category.objects.create(name="Test Category")

    def test_get_by_position(self):
        category = Category.objects.get_by_position(1)
        category_first = Category.objects.first()
        self.assertEqual(category.id, category_first.id)
