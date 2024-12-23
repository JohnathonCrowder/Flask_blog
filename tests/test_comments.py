from test_base import BaseTestCase
from app.models import Comment, Post, User, db
from datetime import datetime, timedelta

class TestComments(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create regular user
        self.user = self.create_user(
            username='regular_user',
            email='user@example.com',
            password='userpass123'
        )
        # Create admin user
        self.admin = self.create_user(
            username='admin_user',
            email='admin@example.com',
            password='adminpass123',
            is_admin=True
        )
        # Create a test post
        self.post = self.create_post(
            title='Test Post',
            content='Test content',
            author=self.admin
        )

    def create_comment(self, content='Test comment', user=None, post=None, created_at=None):
        """Helper method to create a comment"""
        if user is None:
            user = self.user
        if post is None:
            post = self.post
        
        comment = Comment(
            content=content,
            user=user,
            post=post
        )
        if created_at:
            comment.created_at = created_at
        db.session.add(comment)
        db.session.commit()
        return comment

    def test_add_comment(self):
        """Test adding a comment to a post"""
        self.login('user@example.com', 'userpass123')

        response = self.client.post(f'/blog/post/{self.post.id}/comment', data={
            'content': 'This is a test comment'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        comment = Comment.query.filter_by(content='This is a test comment').first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.user_id, self.user.id)
        self.assertEqual(comment.post_id, self.post.id)

    def test_add_comment_empty_content(self):
        """Test adding a comment with empty content"""
        self.login('user@example.com', 'userpass123')

        response = self.client.post(f'/blog/post/{self.post.id}/comment', data={
            'content': ''
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Comment cannot be empty', response.data)

    def test_add_comment_not_logged_in(self):
        """Test that anonymous users cannot comment"""
        with self.client as c:
            # Make sure we're logged out
            c.get('/logout')
            
            # Create or get admin user
            admin = self.create_user(username='admin', email='admin@example.com', 
                                    password='adminpass', is_admin=True)
            
            # Create a post
            post = self.create_post(author=admin)
            
            # Try to comment without being logged in
            response = c.post(f'/blog/post/{post.id}/comment', data={
                'content': 'Anonymous comment'
            }, follow_redirects=False)
            
            self.assert_requires_login(response)

    def test_edit_comment(self):
        """Test editing a comment"""
        comment = self.create_comment('Original comment')
        self.login('user@example.com', 'userpass123')

        response = self.client.post(f'/blog/comment/{comment.id}/edit', 
            json={'content': 'Edited comment'})

        self.assertEqual(response.status_code, 200)
        updated_comment = Comment.query.get(comment.id)
        self.assertEqual(updated_comment.content, 'Edited comment')

    def test_edit_comment_unauthorized(self):
        """Test that users cannot edit others' comments"""
        comment = self.create_comment('Original comment')
        
        # Create and login as different user
        other_user = self.create_user(
            username='other_user',
            email='other@example.com',
            password='otherpass123'
        )
        self.login('other@example.com', 'otherpass123')

        response = self.client.post(f'/blog/comment/{comment.id}/edit', 
            json={'content': 'Edited by other user'})

        self.assertEqual(response.status_code, 403)
        unchanged_comment = Comment.query.get(comment.id)
        self.assertEqual(unchanged_comment.content, 'Original comment')

    def test_delete_comment_as_author(self):
        """Test that users can delete their own comments"""
        comment = self.create_comment('Comment to delete')
        self.login('user@example.com', 'userpass123')

        response = self.client.post(f'/blog/comment/{comment.id}/delete', 
            follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        deleted_comment = Comment.query.get(comment.id)
        self.assertIsNone(deleted_comment)

    def test_delete_comment_as_admin(self):
        """Test that admins can delete any comment"""
        comment = self.create_comment('Comment to delete by admin')
        self.login('admin@example.com', 'adminpass123')

        response = self.client.post(f'/blog/comment/{comment.id}/delete', 
            follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        deleted_comment = Comment.query.get(comment.id)
        self.assertIsNone(deleted_comment)

    def test_delete_comment_unauthorized(self):
        """Test that users cannot delete others' comments"""
        comment = self.create_comment('Comment to not delete')
        
        # Create and login as different user
        other_user = self.create_user(
            username='other_user',
            email='other@example.com',
            password='otherpass123'
        )
        self.login('other@example.com', 'otherpass123')

        response = self.client.post(f'/blog/comment/{comment.id}/delete', 
            follow_redirects=True)

        self.assertEqual(response.status_code, 403)
        comment = Comment.query.get(comment.id)
        self.assertIsNotNone(comment)

    def test_flag_comment(self):
        """Test flagging a comment"""
        comment = self.create_comment('Inappropriate comment')
        self.login('admin@example.com', 'adminpass123')

        response = self.client.post(f'/admin/comment/{comment.id}/toggle-flag')

        self.assertEqual(response.status_code, 200)
        flagged_comment = Comment.query.get(comment.id)
        self.assertTrue(flagged_comment.is_flagged)

    def test_bulk_comment_actions(self):
        """Test bulk actions on comments"""
        comments = [
            self.create_comment(f'Comment {i}') for i in range(3)
        ]
        comment_ids = [str(c.id) for c in comments]
        
        self.login('admin@example.com', 'adminpass123')

        # Test bulk flagging
        response = self.client.post('/admin/comments/bulk-action', data={
            'action': 'flag',
            'comment_ids[]': comment_ids
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        for comment_id in comment_ids:
            comment = Comment.query.get(comment_id)
            self.assertTrue(comment.is_flagged)

        # Test bulk unflagging
        response = self.client.post('/admin/comments/bulk-action', data={
            'action': 'unflag',
            'comment_ids[]': comment_ids
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        for comment_id in comment_ids:
            comment = Comment.query.get(comment_id)
            self.assertFalse(comment.is_flagged)

        # Test bulk deletion
        response = self.client.post('/admin/comments/bulk-action', data={
            'action': 'delete',
            'comment_ids[]': comment_ids
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        for comment_id in comment_ids:
            comment = Comment.query.get(comment_id)
            self.assertIsNone(comment)

    def test_comment_filtering(self):
        """Test comment filtering in admin panel"""
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)

        # Create test users and post
        user = self.create_user(username='regular_user', email='user@example.com', password='password123')
        post = self.create_post(title='Test Post', author=self.admin)

        # Create comments with specific dates
        today_comment = self.create_comment("Today's comment", user=user, post=post)
        today_comment.created_at = now
        yesterday_comment = self.create_comment("Yesterday's comment", user=user, post=post)
        yesterday_comment.created_at = yesterday
        last_week_comment = self.create_comment("Last week's comment", user=user, post=post)
        last_week_comment.created_at = last_week
        
        # Commit the changes to ensure the timestamps are saved
        db.session.commit()

        # Login as admin
        self.login_as_admin()

        # Test "today" filter
        response = self.client.get('/admin/comments?filter=today')
        self.assertEqual(response.status_code, 200)
        
        # Convert HTML entities in the response data
        response_text = response.data.decode('utf-8')
        
        # Add debug prints
        print("\nDebug Information:")
        print(f"Now: {now}")
        print(f"Today's comment created_at: {today_comment.created_at}")
        print(f"Response contains 'Today's comment': {'Today&#39;s comment' in response_text}")
        
        # Use decoded text for assertions
        self.assertIn("Today&#39;s comment", response_text)  # HTML-encoded apostrophe
        self.assertNotIn("Yesterday&#39;s comment", response_text)

        # Test "week" filter
        response = self.client.get('/admin/comments?filter=week')
        self.assertEqual(response.status_code, 200)
        response_text = response.data.decode('utf-8')
        
        self.assertIn("Today&#39;s comment", response_text)
        self.assertIn("Yesterday&#39;s comment", response_text)
        self.assertNotIn("Last week&#39;s comment", response_text)

    def test_comment_search(self):
        """Test searching comments"""
        # Create an admin user
        admin = self.create_user(username='admin', email='admin@example.com', 
                                password='adminpass123', is_admin=True)
        
        # Create a regular user
        user = self.create_user(username='regular', email='regular@example.com',
                            password='regularpass123')
        
        # Create a post
        post = self.create_post(author=admin)
        
        # Create comments with different content
        self.create_comment('Python programming comment', user=user, post=post)
        self.create_comment('JavaScript tutorial comment', user=user, post=post)
        
        # Login as admin
        with self.client as c:
            # First, make sure we're logged out
            c.get('/logout')
            
            # Then login as admin
            response = c.post('/login', data={
                'email': 'admin@example.com',
                'password': 'adminpass123'
            }, follow_redirects=True)
            
            # Now try to search comments
            response = c.get('/admin/comments?search=Python')
            
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Python programming comment', response.data)
            self.assertNotIn(b'JavaScript tutorial comment', response.data)

    def test_comment_pagination(self):
        """Test comment pagination"""
        # Create more comments than the per_page limit 
        user = self.create_user(username='regular_user', email='user@example.com', password='userpass123')
        post = self.create_post(author=self.admin)  # Create a post for the comments
        
        # Create 15 comments (more than default per_page of 10)
        for i in range(15):
            self.create_comment(f'Comment {i}', user=user, post=post)

        # Login as admin to access the admin interface
        self.login_as_admin()

        # Test first page
        response = self.client.get('/admin/comments')
        self.assertEqual(response.status_code, 200)
        # Check for the most recent comment (Comment 14) since they're shown in reverse order
        self.assertIn(b'Comment 14', response.data)

        # Test second page
        response = self.client.get('/admin/comments?page=2')
        self.assertEqual(response.status_code, 200)
        # Check for an earlier comment that should be on the second page
        self.assertIn(b'Comment 4', response.data)

    def test_non_existent_comment(self):
        """Test accessing non-existent comment"""
        self.login('admin@example.com', 'adminpass123')

        response = self.client.post('/blog/comment/99999/delete', 
            follow_redirects=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.post('/blog/comment/99999/edit',
            json={'content': 'Edit non-existent'})
        self.assertEqual(response.status_code, 404)

    def test_comment_with_invalid_post(self):
        """Test commenting on non-existent post"""
        self.login('user@example.com', 'userpass123')

        response = self.client.post('/blog/post/99999/comment', data={
            'content': 'Comment on invalid post'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 404)