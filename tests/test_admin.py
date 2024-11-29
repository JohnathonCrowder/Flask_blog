import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_base import BaseTestCase
from app.models import User, Post, db

class TestAdmin(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.admin = User(username='admin', email='admin@example.com', is_admin=True)
        self.admin.set_password('adminpass123')
        db.session.add(self.admin)
        db.session.commit()

    def test_admin_dashboard_access(self):
        # Login as admin
        self.client.post('/login', data={
            'email': 'admin@example.com',
            'password': 'adminpass123'
        })

        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)

    def test_non_admin_dashboard_access(self):
        # Create regular user
        user = User(username='user', email='user@example.com')
        user.set_password('userpass123')
        db.session.add(user)
        db.session.commit()

        # Login as regular user
        self.client.post('/login', data={
            'email': 'user@example.com',
            'password': 'userpass123'
        })

        response = self.client.get('/admin')
        self.assertNotEqual(response.status_code, 200)