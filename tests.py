import unittest

from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Post
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='jondo')
        u.set_password('default')
        self.assertFalse(u.check_password('wrongpassword'))
        self.assertTrue(u.check_password('default'))

    def test_avatar(self):
        u = User(username='jondo', email='jondo@test.com')
        self.assertEqual(
            u.avatar(128),
            (
                'https://www.gravatar.com/avatar/'
                'c6aaac0b4a947f1d8a1926ccc057ec5a'
                '?d=identicon&s=128'
            )
        )

    def test_follow(self):
        u1 = User(username='jondo', email='jondo@test.com')
        u2 = User(username='janedoe', email='janedoe@test.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'janedoe')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'jondo')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username='user1', email='user1@test.com')
        u2 = User(username='user2', email='user2@test.com')
        u3 = User(username='user3', email='user3@test.com')
        u4 = User(username='user4', email='user4@test.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(
            body="post from user1",
            author=u1,
            timestamp=now + timedelta(seconds=1)
        )
        p2 = Post(
            body="post from user2",
            author=u2,
            timestamp=now + timedelta(seconds=4)
        )
        p3 = Post(
            body="post from user3",
            author=u3,
            timestamp=now + timedelta(seconds=3)
        )
        p4 = Post(
            body="post from user4",
            author=u4,
            timestamp=now + timedelta(seconds=2)
        )
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # user1 follows user2
        u1.follow(u4)  # user1 follows user4
        u2.follow(u3)  # user2 follows user3
        u3.follow(u4)  # user3 follows user4
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
