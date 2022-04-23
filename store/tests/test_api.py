import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BooksAPITestCase(APITestCase):

    def setUp(self):
        # Set up non-modified objects used by all test methods
        self.user = User.objects.create(username='test_username')
        self.user_admin = User.objects.create_superuser(username='admin_username')
        self.book_1 = Book.objects.create(name='First one', price='10.99', author_name='Li', owner=None)
        self.book_2 = Book.objects.create(name='Second book', price='39.99', author_name='John', owner=self.user)
        self.book_3 = Book.objects.create(name='Ho was John', price='25.99', author_name='Mary', owner=None)

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
            'id': self.book_1.id,
            'name': self.book_1.name,
            'price': self.book_1.price,
            'owner': None,
            'author_name': self.book_1.author_name,
            'readers': []
        }
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual(data, response.data)

    def test_try_create_unauthenticated(self):
        url = reverse('book-list')
        data = {
            'name': "It's elso new cool book!",
            'price': '149.99',
            'author_name': 'Martin'
        }
        json_data = json.dumps(data)
        with self.assertRaises(ValueError) as context:
            self.client.post(url, data=json_data, content_type='application/json')

        error_msg = '"Book.owner" must be a "User" instance.'
        self.assertRaises(ValueError)
        self.assertIn(error_msg, str(context.exception))

    def test_create_with_not_correct_field(self):
        self.assertEquals(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            'name': "It's elso new cool book!",
            'price': '123456789.99',
            'author_name': 'Martin'
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(3, Book.objects.all().count())
        expected_data = 'Ensure that there are no more than 7 digits in total.'
        self.assertIn(expected_data, response.data['price'])

    def test_create(self):
        self.assertEquals(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            'name': "It's elso new cool book!",
            'price': '149.99',
            'author_name': 'Martin'
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        self.assertEquals(4, Book.objects.all().count())
        self.assertEquals(self.user, Book.objects.last().owner)

    def test_update_not_owner(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': '299.99',
            'author_name': self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEquals(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEquals(Decimal('10.99'), self.book_1.price)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_2.id,))
        data = {
            'name': self.book_2.name,
            'price': '299.99',
            'author_name': self.book_2.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.book_2.refresh_from_db()
        self.assertEquals(Decimal('299.99'), self.book_2.price)

    def test_update_not_owner_but_staff(self):
        url = reverse('book-detail', args=(self.book_3.id,))
        data = {
            'name': self.book_3.name,
            'price': '299.99',
            'author_name': self.book_3.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user_admin)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.book_3.refresh_from_db()
        self.assertEquals(Decimal('299.99'), self.book_3.price)

    def test_delete_not_owner(self):
        self.assertEquals(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEquals(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEquals(3, Book.objects.all().count())

    def test_delete(self):
        self.assertEquals(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_2.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEquals(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEquals(2, Book.objects.all().count())

    def test_delete_not_owner_but_staff(self):
        self.assertEquals(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_3.id,))
        self.client.force_login(self.user_admin)
        response = self.client.delete(url)
        self.assertEquals(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEquals(2, Book.objects.all().count())


class UserBookRelationAPITestCase(APITestCase):

    def setUp(self):
        # Set up non-modified objects used by all test methods
        self.user1 = User.objects.create(username='test_user1')
        self.user2 = User.objects.create(username='test_user2')
        self.user_admin = User.objects.create_superuser(username='test_admin')
        self.book_1 = Book.objects.create(name='First one', price='10.99', author_name='Li', owner=self.user1)
        self.book_2 = Book.objects.create(name='Second book', price='39.99', author_name='John', owner=self.user1)

    def test_like_then_bookmarks(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'like': True
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user1)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user1, book=self.book_1)
        self.assertTrue(relation.like)
        self.assertFalse(relation.in_bookmarks)
        data = {
            'in_bookmarks': True
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user1, book=self.book_1)
        self.assertTrue(relation.like)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'rate': 2
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user1)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user1, book=self.book_1)
        self.assertEquals(2, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'rate': 6
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user1)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)


class AuthAPITestCase(APITestCase):

    def test_view_auth(self):
        url = 'http://localhost/auth/'
        response = self.client.get(url)
        response_expected = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '<meta charset="UTF-8">',
            '<title>Title</title>',
            '</head>',
            '<body>',
            '<a href="/login/github/">GitHub</a>',
            '</body>',
            '</html>',
        ]
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        for part_expected in response_expected:
            self.assertIn(part_expected, str(response.content), 'Not contain: ' + part_expected)
