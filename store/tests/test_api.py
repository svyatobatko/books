from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer


class BooksAPITestCase(APITestCase):

    def setUp(self):
        # Set up non-modified objects used by all test methods
        self.book_1 = Book.objects.create(name='First one', price=10.99, author_name='Li')
        self.book_2 = Book.objects.create(name='Second book', price=39.99, author_name='John')
        self.book_3 = Book.objects.create(name='Ho was John', price=25.99, author_name='Mary')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serialized_data = BookSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serialized_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 39.99})
        serialized_data = BookSerializer([self.book_2], many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serialized_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'John'})
        serialized_data = BookSerializer([self.book_2, self.book_3], many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serialized_data, response.data)

    def test_get_ordering_author_name_increase(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'author_name'})
        serialized_data = BookSerializer([self.book_2, self.book_1, self.book_3], many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serialized_data, response.data)

    def test_get_ordering_author_name_decrease(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': '-author_name'})
        serialized_data = BookSerializer([self.book_3, self.book_1, self.book_2], many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serialized_data, response.data)

    def test_get_ordering_price_increase(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'price'})
        serialized_data = BookSerializer([self.book_1, self.book_3, self.book_2], many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serialized_data, response.data)

    def test_get_ordering_price_decrease(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': '-price'})
        serialized_data = BookSerializer([self.book_2, self.book_3, self.book_1], many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serialized_data, response.data)
