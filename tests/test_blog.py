from tests.test_base import BaseTestCase
from app import db
from app.models import Post, User

class TestBlog(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Use create_user instead of create_test_user
        self.user = self.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_admin=True
        )

    def test_create_post(self):
        self.login('admin@example.com', 'adminpass123')

        response = self.client.post('/blog/create', data={
            'title': 'Test Post',
            'content': 'This is a test post content',
            'status': 'published',
            'category': 'Technology',
            'subtitle': 'Test Subtitle',
            'tags': 'test,blog'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        post = Post.query.filter_by(title='Test Post').first()
        self.assertIsNotNone(post)
        self.assertEqual(post.content, 'This is a test post content')

    def test_create_post_unauthorized(self):
        # Create and login as a regular user
        regular_user = self.create_test_user(
            username='regular',
            email='regular@example.com',
            password='regularpass123'
        )

        self.login('regular@example.com', 'regularpass123')

        response = self.client.post('/blog/create', data={
            'title': 'Test Post',
            'content': 'This is a test post content',
            'status': 'published'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 403)

    def test_view_post(self):
        post = self.create_post('Test Post', 'Test content', author=self.user)
        response = self.client.get(f'/blog/post/{post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Post', response.data)

    def test_view_draft_post_as_non_admin(self):
        # Create a draft post
        draft_post = self.create_post('Draft Post', 'Draft content', status='draft', author=self.user)

        # Login as regular user
        self.login_as_user()

        # Try to view draft post
        response = self.client.get(f'/blog/post/{draft_post.id}')
        self.assertEqual(response.status_code, 404)

    def test_edit_post(self):
        # Create a post first
        post = self.create_post('Original Title', 'Original content', author=self.user)
        
        # Login as admin
        self.login('admin@example.com', 'adminpass123')

        # Try to edit the post
        response = self.client.post(f'/blog/edit/{post.id}', data={
            'title': 'Updated Title',
            'content': 'Updated content',
            'status': 'published',
            'category': 'Technology',
            'subtitle': 'Updated Subtitle',
            'tags': 'updated,blog'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        updated_post = Post.query.get(post.id)
        self.assertEqual(updated_post.title, 'Updated Title')
        self.assertEqual(updated_post.content, 'Updated content')