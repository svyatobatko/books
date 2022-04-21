from django.test import TestCase

from store.models import Book
from store.serializers import BookSerializer


class BooksSerializerTestCase(TestCase):
    def test_book_serializer_ok(self):
        book_1 = Book.objects.create(name='First one', price=10.99)
        book_2 = Book.objects.create(name='Second book', price=19.99)
        serialized_data = BookSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'First one',
                'price': '10.99'
            },
            {
                'id': book_2.id,
                'name': 'Second book',
                'price': '19.99'
            },
        ]
        self.assertEquals(expected_data, serialized_data)
