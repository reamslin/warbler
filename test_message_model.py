"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes
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

class MessageModelTestCase(TestCase):
    """tests model for messages"""

    def setUp(self):
        """set up test client and smaple data"""
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

        self.m = Message(
            text =  "This is important",
            user_id = self.u1.id
        )

        db.session.add(self.m)
        db.session.commit()
    
    def test_basic_model(self):
        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(self.u1.messages[0].text, "This is important")

    def test_likes(self):
        
       l = Likes(
           user_id = self.u1.id,
            message_id = self.m.id)
       db.session.add(l)
       db.session.commit()

       self.assertEqual(len(self.u1.likes), 1)
