from django.test import TestCase

from store.models import Book


class BookModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Book.objects.create(name='Test book', price='999.99')

    def test_book_name_label(self):
        book = Book.objects.get(name='Test book')
        field_label = book._meta.get_field('name').verbose_name
        self.assertEquals('name', field_label)

    def test_book_price_label(self):
        book = Book.objects.get(name='Test book')
        field_label = book._meta.get_field('price').verbose_name
        self.assertEquals('price', field_label)

    def test_book_name_max_length(self):
        book = Book.objects.get(name='Test book')
        max_length = book._meta.get_field('name').max_length
        self.assertEquals(max_length, 255)

    def test_book_price_max_digits(self):
        book = Book.objects.get(name='Test book')
        max_digits = book._meta.get_field('price').max_digits
        self.assertEquals(max_digits, 7)

    def test_book_price_decimal_places(self):
        book = Book.objects.get(name='Test book')
        decimal_places = book._meta.get_field('price').decimal_places
        self.assertEquals(decimal_places, 2)

