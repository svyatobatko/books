from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Book, UserBookRelation


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

    def test_book_owner_label(self):
        field_label = self.book._meta.get_field('owner').verbose_name
        self.assertEquals('owner', field_label)

    def test_book_readers_label(self):
        field_label = self.book._meta.get_field('readers').verbose_name
        self.assertEquals('readers', field_label)

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


class UserBookRelationModelTest(TestCase):

    def setUp(self):
        # Set up non-modified objects used by all test methods
        self.user = User.objects.create(username="test_user")
        self.book = Book.objects.create(name='Test book', price='999.99', author_name='Li')
        self.relation = UserBookRelation.objects.create(user=self.user, book=self.book, rate=3)

    def test_user_book_relation_user_label(self):
        field_label = self.relation._meta.get_field('user').verbose_name
        self.assertEquals('user', field_label)

    def test_user_book_relation_book_label(self):
        field_label = self.relation._meta.get_field('book').verbose_name
        self.assertEquals('book', field_label)

    def test_user_book_relation_like_label(self):
        field_label = self.relation._meta.get_field('like').verbose_name
        self.assertEquals('like', field_label)

    def test_user_book_relation_in_bookmarks_label(self):
        field_label = self.relation._meta.get_field('in_bookmarks').verbose_name
        self.assertEquals('in bookmarks', field_label)

    def test_user_book_relation_rate_label(self):
        field_label = self.relation._meta.get_field('rate').verbose_name
        self.assertEquals('rate', field_label)

    def test_user_book_relation_get_str(self):
        expected_result = f'{self.user.username}: {self.book}, RATE: {self.relation.rate}'
        self.assertEquals(expected_result, str(self.relation))
