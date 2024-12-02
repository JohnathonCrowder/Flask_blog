import unittest
from flask import abort, render_template
from app import create_app, db
from app.models import User, Post

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_user(self, username='testuser', email='test@example.com', password='password', is_admin=False):
        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def create_post(self, title='Test Post', content='Test Content', author=None, status='published'):
        if not author:
            author = self.create_user()
        post = Post(title=title, content=content, author=author, status=status)
        db.session.add(post)
        db.session.commit()
        return post

    def login(self, email='test@example.com', password='password'):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Update assertion to match actual HTML content
        self.assertIn(b'Featured Articles', response.data)
        self.assertIn(b'Latest Posts', response.data)

    def test_about_route(self):
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        # Update assertion to match actual HTML content
        self.assertIn(b'About CodeVault', response.data)
        self.assertIn(b'Our Mission', response.data)

    def test_user_dashboard_route(self):
        self.create_user()
        self.login()
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        # Update assertion to match actual HTML content
        self.assertIn(b'Featured Posts', response.data)
        self.assertIn(b'Recent Posts', response.data)

    def test_subscribe_route(self):
        with self.client as c:
            response = c.post('/subscribe', data={
                'email': 'subscriber@example.com'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # Check for redirect
            self.assertIn(b'Thank you for subscribing!', response.data)

    def test_search_route(self):
        # Create a test post first
        post = self.create_post(title='Searchable Post', content='This is searchable content')
        
        response = self.client.get('/search?q=searchable')
        self.assertEqual(response.status_code, 200)
        # Update assertion to match actual search results template
        self.assertIn(b'Search Results', response.data)

    def test_manage_account_change_password(self):
        user = self.create_user()
        with self.client as c:
            self.login()
            response = c.post('/manage-account', data={
                'action': 'change_password',
                'current_password': 'password',
                'new_password': 'newpassword',
                'confirm_password': 'newpassword'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Your password has been updated successfully', response.data)

    def test_manage_account_delete_account(self):
        self.create_user()
        with self.client as c:
            self.login()
            response = c.post('/manage-account', data={
                'action': 'delete_account',
                'delete_password': 'password'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Your account has been deleted successfully', response.data)

    def test_internal_server_error(self):
        # Create a custom error handler for 500 errors
        @self.app.errorhandler(500)
        def internal_error(error):
            return render_template('errors/500.html'), 500

        # Create a route that will trigger a 500 error
        @self.app.route('/error-test')
        def error_test():
            abort(500)

        response = self.client.get('/error-test')
        self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()