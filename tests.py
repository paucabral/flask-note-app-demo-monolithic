import unittest
from app import app, db, Note, User
import os
from dotenv import load_dotenv

load_dotenv()

class NoteAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()

        user = User(username=os.getenv("TEST_USER"))
        user.set_password(os.getenv("TEST_PASSWORD"))
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

    def tearDown(self):
        db.drop_all()
        db.session.remove()

    def test_create_note(self):
        # Login the user
        response = self.client.post('/', data={
            'username': os.getenv("TEST_USER"),
            'password': os.getenv("TEST_PASSWORD")
        }, follow_redirects = True)
        self.assertEqual(response.status_code, 200)

        # Create a note
        response = self.client.post('/notes', data={
            'title': 'Test Note',
            'content': 'This is a test note'
        }, follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Note.query.all()), 1)
        note = Note.query.first()
        self.assertEqual(note.title, 'Test Note')
        self.assertEqual(note.content, 'This is a test note')
        self.assertEqual(note.user_id, self.user_id)
        
if __name__ == '__main__':
    unittest.main()