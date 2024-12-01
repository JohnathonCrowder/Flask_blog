import unittest
from unittest.mock import patch, MagicMock
from flask.cli import ScriptInfo
from app import create_app, db
from app.models import User
from app.commands import create_admin, init_app
import logging

class TestCommands(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('app.commands.logger.info')
    def test_create_admin_success(self, mock_info):
        runner = self.app.test_cli_runner()
        result = runner.invoke(create_admin, ['testadmin', 'admin@test.com', 'password123'])

        self.assertEqual(result.exit_code, 0)
        self.assertIn('Admin user testadmin created successfully.', result.output)

        user = User.query.filter_by(username='testadmin').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.is_admin)
        self.assertEqual(user.email, 'admin@test.com')
        self.assertTrue(user.check_password('password123'))

        mock_info.assert_any_call("Attempting to create admin user: testadmin")
        mock_info.assert_any_call("User object created")
        mock_info.assert_any_call("Password set")
        mock_info.assert_any_call("User added to session")
        mock_info.assert_any_call("Session committed")

    @patch('app.commands.logger.info')
    def test_create_admin_duplicate_username(self, mock_info):
        # Create a user with the same username first
        user = User(username='testadmin', email='existing@test.com', is_admin=True)
        user.set_password('existingpass')
        db.session.add(user)
        db.session.commit()

        runner = self.app.test_cli_runner()
        result = runner.invoke(create_admin, ['testadmin', 'new@test.com', 'newpass123'])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Username 'testadmin' already exists.", result.output)
        mock_info.assert_any_call("IntegrityError caught: UNIQUE constraint failed: user.username")

    @patch('app.commands.logger.info')
    def test_create_admin_duplicate_email(self, mock_info):
        # Create a user with the same email first
        user = User(username='existinguser', email='admin@test.com', is_admin=True)
        user.set_password('existingpass')
        db.session.add(user)
        db.session.commit()

        runner = self.app.test_cli_runner()
        result = runner.invoke(create_admin, ['newadmin', 'admin@test.com', 'newpass123'])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Email 'admin@test.com' already exists.", result.output)
        mock_info.assert_any_call("IntegrityError caught: UNIQUE constraint failed: user.email")

    @patch('app.commands.db.session.commit')
    @patch('app.commands.logger.info')
    def test_create_admin_unexpected_error(self, mock_info, mock_commit):
        mock_commit.side_effect = Exception("Unexpected error")

        runner = self.app.test_cli_runner()
        result = runner.invoke(create_admin, ['testadmin', 'admin@test.com', 'password123'])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("An error occurred: Unexpected error", result.output)
        mock_info.assert_any_call("Unexpected error: Unexpected error")

    @patch('app.commands.logger.info')
    def test_init_app(self, mock_info):
        mock_app = MagicMock()
        init_app(mock_app)
        mock_app.cli.add_command.assert_called_once_with(create_admin)
        mock_info.assert_called_once_with("Initializing admin command")

if __name__ == '__main__':
    unittest.main()