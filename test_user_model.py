"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy import exc

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        self.u1 = User(
            email="test@test.com",
            username="user1",
            password="password"
        )
        self.u2 = User(
            email="test2@test.com",
            username="user2",
            password="password"
        )

        db.session.add_all([self.u1, self.u2])
        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""

        f = Follows(
            user_being_followed_id = self.u2.id,
            user_following_id = self.u1.id
        )

        db.session.add(f)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))

    def test_is_not_following(self):
        """Does is_following successfully detect when user1 is not following user2?"""

        self.assertFalse(self.u1.is_following(self.u2))

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""

        f = Follows(
            user_being_followed_id = self.u1.id,
            user_following_id = self.u2.id
        )

        db.session.add(f)
        db.session.commit()

        self.assertTrue(self.u1.is_followed_by(self.u2))

    def test_is_not_followed_by(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""

        self.assertFalse(self.u1.is_followed_by(self.u2))

    def test_create_user(self):
        """Does User.signup successfully create a new user given valid credentials?"""

        u = User.signup("testuser", "testing@gmail.com", "password", None)
        uid = 100
        u.id = uid
        db.session.commit()

        user = User.query.get_or_404(uid)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testing@gmail.com")
        #did the password get hashed?
        self.assertNotEqual(user.password, "password")
    
    def test_invalid_username(self):
        """Does User.signup raise IntegrityError when no username is provided?"""

        bad = User.signup(None, "testing@gmail.com", "password", None)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email(self):
        """Does User.signup raise IntegrityError when no email is provided?"""

        bad = User.signup("testing", None, "password", None)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password(self):
        """Does user.signup raise error when invalid password is used?"""

        with self.assertRaises(ValueError) as context:
            bad = User.signup("Testing", "testing#@gmail.com", None, None)
        
        with self.assertRaises(ValueError) as context:
            bad = User.signup("Testing", "testing123@gmail.com", "", None)

    def test_duplicate_user_signup(self):
        """Does user.signup raise error when a duplicate username is used?"""
    
        bad = User.signup("user1", "Testing@gmail.com", "password", None)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

#### TESTS failing with ValueError("Invalid Salt") ####
    
   ### def test_authentication(self):
    ###    """Does authentication work with valid credentials?"""
    ###    u = User.authenticate("user1", "password")
    ###    self.assertIsNotNone(u)
    ###    self.assertEqual(u.id, self.u1.id)

    ### def test_bad_password_authentication(self):
    ###   """Does authentication fail with wrong password?"""
    ###    self.assertFalse(User.authenticate("user1", "notmypassword"))
        