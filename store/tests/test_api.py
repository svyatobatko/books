from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer


class BooksAPITestCase(APITestCase):
    def test_get(self):
        book_1 = Book.objects.create(name='First one', price=10.99)
        book_2 = Book.objects.create(name='Second book', price=19.99)
        url = reverse('book-list')
        response = self.client.get(url)
        serialized_data = BookSerializer([book_1, book_2], many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serialized_data, response.data)
