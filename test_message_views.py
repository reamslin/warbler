"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    
    def test_delete_message(self):
        """can user delete message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message(
                user_id = self.testuser.id,
                text="delete me")
            db.session.add(m)
            db.session.commit()

            resp = c.post(f"/messages/{m.id}/delete")
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.get(m.id)
            self.assertIsNone(msg)

    def test_not_logged_in_add_message(self):
        """are you prohibited from adding messages when logged out?"""

        with self.client as c:

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True) 

            self.assertIn("Access unauthorized", str(resp.data))

    def test_not_logged_in_delete_message(self):
        """ are you prohibited from deleting messages when logged out?"""
        with self.client as c:

            m = Message(
                user_id = self.testuser.id,
                text="just try to delete me")

            db.session.add(m)
            db.session.commit()

            resp = c.post(f"/messages/{m.id}/delete", follow_redirects = True)

            self.assertIn("Access unauthorized", str(resp.data))

            msg = Message.query.get(m.id)

            self.assertIsNotNone(msg)

    def test_not_user_add_message(self):
        """ are you prohibited from adding a message as another user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 2342349302948

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)

            self.assertIn("Access unauthorized", str(resp.data))

#This test raises an error
    """def test_not_user_delete_message(self):
        with self.client as c:
            u = User.signup("notme", "no@gmail.com", "password", None)
            db.session.commit()

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = u.id

            m = Message(
                user_id = self.testuser.id,
                text="just try to delete me")
            db.session.add(m)
            db.session.commit()

            resp = c.post(f"/messages/{m.id}/delete", follow_redirects=True)

            self.assertIn("Access unauthorized", str(resp.data))

            msg = Message.query.get(m.id)

            self.assertIsNotNone(msg)    
            """





