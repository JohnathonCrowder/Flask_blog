import unittest
import os
import sys
from datetime import datetime

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Post, Comment, SiteSettings

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up any necessary test fixtures that can be reused across tests"""
        cls.app = create_app()
        cls.app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key',
            'SERVER_NAME': 'localhost.localdomain'
        })

    def setUp(self):
        """Set up test client and database for each test"""
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create all database tables
        db.create_all()
        
        # Initialize site settings
        self.init_site_settings()

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def init_site_settings(self):
        """Initialize default site settings"""
        settings = SiteSettings(
            site_name='Test Site',
            site_description='Test Description',
            contact_email='test@example.com',
            posts_per_page=10,
            maintenance_mode=False,
            allow_registration=True
        )
        db.session.add(settings)
        db.session.commit()

    # User Helper Methods
    def create_user(self, username='testuser', email='test@example.com', 
                password='password123', is_admin=False):
        """Create a test user or return existing one"""
        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(username=username, email=email, is_admin=is_admin)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
        return user

    def create_admin(self, username='admin', email='admin@example.com', 
                    password='adminpass123'):
        """Create an admin user"""
        return self.create_user(username=username, email=email, 
                              password=password, is_admin=True)

    def login(self, email, password):
        """Log in a user"""
        return self.client.post('/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        """Log out the current user"""
        return self.client.get('/logout', follow_redirects=True)

    # Post Helper Methods
    def create_post(self, title='Test Post', content='Test Content', 
                author=None, status='published', category='Test Category',
                tags='test,sample'):
        """Create a test post"""
        if author is None:
            author = self.create_user()  # This will now return existing user if any
        
        post = Post(
            title=title,
            content=content,
            status=status,
            category=category,
            tags=tags,
            author=author
        )
        db.session.add(post)
        db.session.commit()
        return post

    def create_draft(self, title='Draft Post', content='Draft Content', 
                    author=None):
        """Create a draft post"""
        return self.create_post(title=title, content=content, 
                              author=author, status='draft')

    # Comment Helper Methods
    def create_comment(self, content='Test Comment', user=None, post=None):
        """Create a test comment"""
        if user is None:
            user = self.create_user()
        if post is None:
            post = self.create_post()
        
        comment = Comment(
            content=content,
            user=user,
            post=post
        )
        db.session.add(comment)
        db.session.commit()
        return comment
    
    def login_user(self, user=None):
        if user is None:
            user = self.create_user('testuser', 'test@example.com', 'password123')
        return self.client.post('/login', data={
            'email': user.email,
            'password': 'password123'
        }, follow_redirects=True)

    # Authentication Helper Methods
    def login_as_admin(self):
        """Create and log in as an admin user"""
        admin = self.create_admin()
        return self.login('admin@example.com', 'adminpass123')

    def login_as_user(self):
        """Create and log in as a regular user"""
        user = self.create_user()
        return self.login('test@example.com', 'password123')

    # Assertion Helper Methods
    def assert_flashed(self, response, message, category='message'):
        """Assert that a message was flashed"""
        self.assertIn(message.encode(), response.data)

    def assert_redirects(self, response, location):
        """Assert that response redirects to a specific location"""
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, location)

    def assert_requires_login(self, response):
        """Assert that the response requires login"""
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.startswith('/login'))

    def assert_requires_admin(self, response):
        """Assert that the response requires admin privileges"""
        self.assertEqual(response.status_code, 403)

    # Database Helper Methods
    def refresh(self, obj):
        """Refresh an object from the database"""
        db.session.refresh(obj)
        return obj

    def count_models(self, model):
        """Count the number of instances of a model"""
        return model.query.count()

    # Site Settings Helper Methods
    def update_site_settings(self, **kwargs):
        """Update site settings"""
        settings = SiteSettings.query.first()
        for key, value in kwargs.items():
            setattr(settings, key, value)
        db.session.commit()
        return settings

    # Content Generation Helper Methods
    def generate_dummy_content(self, num_users=3, num_posts=5, num_comments=10):
        """Generate dummy content for testing"""
        users = [self.create_user(f'user{i}', f'user{i}@example.com') 
                for i in range(num_users)]
        
        posts = []
        for i in range(num_posts):
            author = users[i % len(users)]
            post = self.create_post(
                title=f'Post {i}',
                content=f'Content for post {i}',
                author=author
            )
            posts.append(post)

        comments = []
        for i in range(num_comments):
            user = users[i % len(users)]
            post = posts[i % len(posts)]
            comment = self.create_comment(
                content=f'Comment {i}',
                user=user,
                post=post
            )
            comments.append(comment)

        return users, posts, comments

    # Utility Methods
    def get_context_variable(self, response, variable_name):
        """Get a variable from the template context"""
        with self.app.test_request_context():
            template = self.app.jinja_env.from_string(
                "{{ " + variable_name + " }}"
            )
            return template.render(response._get_context_locals())

    def create_test_image(self, filename='test.jpg'):
        """Create a test image file"""
        from io import BytesIO
        from PIL import Image
        
        file = BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'JPEG')
        file.seek(0)
        return file

    def upload_test_image(self, endpoint, image_field='image', **data):
        """Upload a test image to an endpoint"""
        image = self.create_test_image()
        data[image_field] = (image, 'test.jpg')
        return self.client.post(endpoint, 
                              data=data,
                              content_type='multipart/form-data',
                              follow_redirects=True)