import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer


class BooksAPITestCase(APITestCase):

    def setUp(self):
        # Set up non-modified objects used by all test methods
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='First one', price='10.99', author_name='Li')
        self.book_2 = Book.objects.create(name='Second book', price='39.99', author_name='John')
        self.book_3 = Book.objects.create(name='Ho was John', price='25.99', author_name='Mary')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serialized_data = BookSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serialized_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': '39.99'})
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

    def test_get_one_book(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        response = self.client.get(url, content_type='application/json')
        data = {
            "id": self.book_1.id,
            "name": self.book_1.name,
            "price": self.book_1.price,
            "author_name": self.book_1.author_name
        }
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual(data, response.data)

    def test_try_create_unauthenticated(self):
        url = reverse('book-list')
        data = {
            "name": "It's elso new cool book!",
            "price": "149.99",
            "author_name": "Martin"
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEquals(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_create_with_not_correct_field(self):
        self.assertEquals(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "It's elso new cool book!",
            "price": "123456789.99",
            "author_name": "Martin"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(3, Book.objects.all().count())
        expected_data = "Ensure that there are no more than 7 digits in total."
        self.assertIn(expected_data, response.data['price'])

    def test_create(self):
        self.assertEquals(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "It's elso new cool book!",
            "price": "149.99",
            "author_name": "Martin"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        self.assertEquals(4, Book.objects.all().count())

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": "299.99",
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEquals(Decimal('299.99'), self.book_1.price)

    def test_delete(self):
        self.assertEquals(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEquals(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEquals(2, Book.objects.all().count())
