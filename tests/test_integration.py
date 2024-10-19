import pytest
from flask import url_for
import os
import sys

# Append the project path to the system path
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, ".."))

from views import app, db
from models import User, Note

class TestIntegration:

    @pytest.fixture(autouse=True)
    def setUp(self):
        """Set up the test environment"""
        self.app = app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create a test user
        self.test_user = User(username=os.getenv("TEST_USER"))
        self.test_user.set_password(os.getenv("TEST_PASSWORD"))
        db.session.add(self.test_user)
        db.session.commit()

        yield

        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password):
        """Helper function to log in"""
        return self.client.post(
            "/",
            data={'username': username, 'password': password},
            follow_redirects=True
        )

    def logout(self):
        """Helper function to log out"""
        return self.client.get("/logout", follow_redirects=True)

    def test_login_logout(self):
        """Test the login and logout process"""
        response = self.login(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))
        assert response.status_code == 200
        assert b"Note" in response.data

        response = self.logout()
        assert response.status_code == 200

    def test_create_note(self):
        """Test creating a note"""
        self.login(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))

        response = self.client.post(
            "/notes",
            data = {
                    'title': 'New Note',
                    'content': 'A test note'
                    },
            follow_redirects=True
        )
        assert response.status_code == 200

        # Check if the note was added to the database
        note = Note.query.filter_by(title='New Note').first()
        assert note is not None

    def test_read_notes(self):
        """Test reading notes"""
        self.login(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))

        # Create a note first
        self.client.post(
            "/notes",
            data = {
                    'title': 'New Note',
                    'content': 'A test note'
                    },
            follow_redirects=True
        )

        response = self.client.get("/notes")
        assert response.status_code == 200

    def test_update_note(self):
        """Test updating a note"""
        self.login(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))

        # Create a note
        note = Note(title="Old Title", content="Old Content", user_id=self.test_user.id)
        db.session.add(note)
        db.session.commit()

        response = self.client.post(
            f"/notes/{note.id}",
            data = {
                    'title': 'Updated Title',
                    'content': 'Updated Content'
                    },
            follow_redirects=True
        )
        assert response.status_code == 200

        # Verify that the update was successful
        updated_note = db.session.get(Note, note.id)
        assert updated_note.title == 'Updated Title'

    def test_delete_note(self):
        """Test deleting a note"""
        self.login(os.getenv("TEST_USER"), os.getenv("TEST_PASSWORD"))

        # Create a note
        note = Note(title="Delete Me", content="To be deleted", user_id=self.test_user.id)
        db.session.add(note)
        db.session.commit()

        # Delete the note
        response = self.client.get(
            f"/notes/{note.id}/delete",
            follow_redirects=True
        )
        assert response.status_code == 200

        # Verify that the note was deleted
        deleted_note = db.session.get(Note, note.id)
        assert deleted_note is None

if __name__ == '__main__':
    pytest.main()