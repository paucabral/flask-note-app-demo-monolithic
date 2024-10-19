import unittest

from dotenv import load_dotenv
load_dotenv()

import os
import sys

# Append the project path to the system path
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, ".."))

from views import app
from models import db, User, Note

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
    
    def test_get_all_notes(self):
        # Login the user
        response = self.client.post('/', data={
            'username': os.getenv("TEST_USER"),
            'password': os.getenv("TEST_PASSWORD")
        }, follow_redirects = True)
        self.assertEqual(response.status_code, 200)

        # Create Note
        note = Note(title='Test Note', content='This is a test note', user_id=self.user_id)
        db.session.add(note)
        db.session.commit()

        # Get all notes
        response = self.client.get('/notes', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Note', response.data)

    def test_get_note(self):
        # Login the user
        response = self.client.post('/', data={
            'username': os.getenv("TEST_USER"),
            'password': os.getenv("TEST_PASSWORD")
        }, follow_redirects = True)
        self.assertEqual(response.status_code, 200)

        # Create Note
        note = Note(title='Test Note', content='This is a test note', user_id=self.user_id)
        db.session.add(note)
        db.session.commit()

        # Get create note
        response = self.client.get(f'/notes/{note.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Note', response.data)
    
    def test_update_note(self):
        # Login the user
        response = self.client.post('/', data={
            'username': os.getenv("TEST_USER"),
            'password': os.getenv("TEST_PASSWORD")
        }, follow_redirects = True)
        self.assertEqual(response.status_code, 200)

        # Create Note
        note = Note(title='Test Note', content='This is a test note', user_id=self.user_id)
        db.session.add(note)
        db.session.commit()

        # Update a note
        response = self.client.post(f'/notes/{note.id}', data={
            'title': "Updated Note",
            'content': "Updated content"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        updated_note = db.session.get(Note, note.id)
        self.assertEqual(updated_note.title, "Updated Note")
        self.assertEqual(updated_note.content, "Updated content")

    def test_delete_note(self):
        # Login the user
        response = self.client.post('/', data={
            'username': os.getenv("TEST_USER"),
            'password': os.getenv("TEST_PASSWORD")
        }, follow_redirects = True)
        self.assertEqual(response.status_code, 200)

        # Create Note
        note = Note(title='Test Note', content='This is a test note', user_id=self.user_id)
        db.session.add(note)
        db.session.commit()

        response = self.client.get(f'/notes/{note.id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Note.query.all()), 0)
        
if __name__ == '__main__':
    unittest.main()