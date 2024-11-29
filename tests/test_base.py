import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Post, Comment

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def create_test_user(self, username='testuser', email='test@example.com', password='testpass123', is_admin=False):
        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def create_post(self, title, content, status='published', author=None, category='Technology', tags='test'):
        if author is None:
            author = self.create_test_user(is_admin=True)
        post = Post(
            title=title,
            content=content,
            status=status,
            author=author,
            category=category,
            tags=tags
        )
        db.session.add(post)
        db.session.commit()
        return post

    def login(self, email, password):
        return self.client.post('/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def login_as_admin(self):
        admin = self.create_test_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_admin=True
        )
        return self.login('admin@example.com', 'adminpass123')

    def login_as_user(self):
        user = self.create_test_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )
        return self.login('user@example.com', 'userpass123')