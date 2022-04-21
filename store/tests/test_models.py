from django.test import TestCase

from store.models import Book


class BookModelTest(TestCase):

    def setUp(self):
        # Set up non-modified objects used by all test methods
        self.book = Book.objects.create(name='Test book', price='999.99', author_name='Li')

    def test_book_name_label(self):
        field_label = self.book._meta.get_field('name').verbose_name
        self.assertEquals('name', field_label)

    def test_book_price_label(self):
        field_label = self.book._meta.get_field('price').verbose_name
        self.assertEquals('price', field_label)

    def test_book_author_name_label(self):
        field_label = self.book._meta.get_field('author_name').verbose_name
        self.assertEquals('author name', field_label)

    def test_book_name_max_length(self):
        max_length = self.book._meta.get_field('name').max_length
        self.assertEquals(max_length, 255)

    def test_book_author_name_max_length(self):
        max_length = self.book._meta.get_field('author_name').max_length
        self.assertEquals(max_length, 255)

    def test_book_price_max_digits(self):
        max_digits = self.book._meta.get_field('price').max_digits
        self.assertEquals(max_digits, 7)

    def test_book_price_decimal_places(self):
        decimal_places = self.book._meta.get_field('price').decimal_places
        self.assertEquals(decimal_places, 2)

