from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer, UserBookRelationSerializer


class BooksSerializerTestCase(TestCase):
    def test_book_serializer_ok(self):
        book_1 = Book.objects.create(name='First one', price=10.99, author_name='Li')
        book_2 = Book.objects.create(name='Second book', price=19.99, author_name='John')
        serialized_data = BookSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'First one',
                'author_name': 'Li',
                'price': '10.99',
                'likes_count': 0
            },
            {
                'id': book_2.id,
                'name': 'Second book',
                'author_name': 'John',
                'price': '19.99',
                'likes_count': 0
            },
        ]
        self.assertEquals(expected_data, serialized_data, serialized_data)

    def test_book_serializer_with_likes_ok(self):
        user_1 = User.objects.create(username="test_user1")
        user_2 = User.objects.create(username="test_user2")
        user_3 = User.objects.create(username="test_user3")
        book_1 = Book.objects.create(name='First one', price=10.99, author_name='Li')
        book_2 = Book.objects.create(name='Second book', price=19.99, author_name='John')

        UserBookRelation.objects.create(user=user_1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user_2, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user_3, book=book_1, like=True, rate=4)

        UserBookRelation.objects.create(user=user_1, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user_2, book=book_2, like=True, rate=4)
        UserBookRelation.objects.create(user=user_3, book=book_2, like=False)

        books = Book.objects.all().annotate(annotated_likes_count=Count(Case(When(userbookrelation__like=True,
                                                                                  then=1))),
                                            rating=Avg('userbookrelation__rate')
                                            ).order_by('id')
        serialized_data = BookSerializer(books, many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'First one',
                'author_name': 'Li',
                'price': '10.99',
                'likes_count': 3,
                'annotated_likes_count': 3,
                'rating': '4.67'
            },
            {
                'id': book_2.id,
                'name': 'Second book',
                'author_name': 'John',
                'price': '19.99',
                'likes_count': 2,
                'annotated_likes_count': 2,
                'rating': '3.50'
            },
        ]
        self.assertEquals(expected_data, serialized_data, serialized_data)


class UserBookRelationSerializerTestCase(TestCase):
    def test_user_book_relation_serializer_ok(self):
        user_1 = User.objects.create(username="test_user")
        book_1 = Book.objects.create(name='First one', price=10.99, author_name='Li')
        book_2 = Book.objects.create(name='Second book', price=19.99, author_name='John')
        relation_1 = UserBookRelation.objects.create(user=user_1, book=book_1)
        relation_2 = UserBookRelation.objects.create(user=user_1, book=book_2)
        serialized_data = UserBookRelationSerializer([relation_1, relation_2], many=True).data
        expected_data = [
            {
                'book': book_1.id,
                'like': False,
                'in_bookmarks': False,
                'rate': None
            },
            {
                'book': book_2.id,
                'like': False,
                'in_bookmarks': False,
                'rate': None
            },
        ]
        self.assertEqual(expected_data, serialized_data, serialized_data)
