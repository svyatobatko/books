from unittest import TestCase

from django.contrib.auth.models import User

from store.logic import set_rating
from store.models import UserBookRelation, Book


class SetRatingTestCase(TestCase):
    def setUp(self):
        user_1 = User.objects.create(username='test_user1', first_name='User1', last_name='User1', email='e1@ma.il')
        user_2 = User.objects.create(username='test_user2', first_name='User2', last_name='User2', email='e2@ma.il')
        user_3 = User.objects.create(username='test_user3', first_name='User3', last_name='User3', email='e3@ma.il')
        self.book_1 = Book.objects.create(name='First one', price=10.99, author_name='Li', owner=user_1)

        UserBookRelation.objects.create(user=user_1, book=self.book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user_2, book=self.book_1, like=True, rate=5)
        user_book_relation_3 = UserBookRelation.objects.create(user=user_3, book=self.book_1, like=True)
        user_book_relation_3.rate = 4
        user_book_relation_3.save()

    def test_rating_ok(self):
        self.book_1.refresh_from_db()
        self.assertEqual('4.67', str(self.book_1.rating))
