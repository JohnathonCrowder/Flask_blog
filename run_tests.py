import unittest
import sys
import os
import coverage
from datetime import datetime
from flask_migrate import upgrade

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize coverage reporting
COV = coverage.Coverage(
    branch=True,
    include='app/*',
    omit=[
        'app/templates/*',
        'tests/*',
        '*/migrations/*'
    ]
)
COV.start()

from app import create_app, db
from app.models import User, Post, Comment, SiteSettings

class TestDatabaseManager:
    def __init__(self, app):
        self.app = app

    def init_db(self):
        """Initialize the test database"""
        with self.app.app_context():
            # Create all tables
            db.create_all()

    def cleanup_db(self):
        """Clean up the test database"""
        with self.app.app_context():
            # Drop all tables
            db.session.remove()
            db.drop_all()

    def reset_db(self):
        """Reset the test database to a clean state"""
        self.cleanup_db()
        self.init_db()

    def create_test_data(self):
        """Create initial test data"""
        with self.app.app_context():
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('adminpass123')
            db.session.add(admin)

            # Create regular user
            user = User(
                username='user',
                email='user@example.com'
            )
            user.set_password('userpass123')
            db.session.add(user)

            # Create some test posts
            post1 = Post(
                title='Test Post 1',
                content='Content for test post 1',
                status='published',
                author=admin
            )
            post2 = Post(
                title='Test Post 2',
                content='Content for test post 2',
                status='draft',
                author=admin
            )
            db.session.add_all([post1, post2])

            # Create some test comments
            comment1 = Comment(
                content='Test comment 1',
                user=user,
                post=post1
            )
            comment2 = Comment(
                content='Test comment 2',
                user=admin,
                post=post1
            )
            db.session.add_all([comment1, comment2])

            # Create initial site settings
            settings = SiteSettings(
                site_name='Test Site',
                site_description='Test Description',
                posts_per_page=10
            )
            db.session.add(settings)

            # Commit the changes
            db.session.commit()

def setup_test_environment():
    """Set up the test environment"""
    # Create test app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    # Initialize test database manager
    db_manager = TestDatabaseManager(app)
    return app, db_manager

def run_tests():
    """Run the test suite"""
    # Set up test environment
    app, db_manager = setup_test_environment()

    try:
        # Initialize database
        db_manager.init_db()

        # Discover and run tests
        tests = unittest.TestLoader().discover('tests', pattern='test_*.py')
        
        # Run tests with verbosity
        result = unittest.TextTestRunner(verbosity=2).run(tests)

        if COV:
            # Generate coverage report
            COV.stop()
            COV.save()
            print('Coverage Summary:')
            COV.report()
            
            # Generate HTML coverage report
            basedir = os.path.abspath(os.path.dirname(__file__))
            covdir = os.path.join(basedir, 'coverage')
            COV.html_report(directory=covdir)
            print(f'HTML version: file://{covdir}/index.html')
            
            COV.erase()

        return result.wasSuccessful()

    finally:
        # Clean up
        db_manager.cleanup_db()

def profile_tests():
    """Run tests with profiling"""
    import cProfile
    import pstats
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    success = run_tests()
    
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats(50)  # Print top 50 time-consuming operations
    
    return success

if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Run the test suite')
    parser.add_argument('--coverage', action='store_true', help='Run tests with coverage reporting')
    parser.add_argument('--profile', action='store_true', help='Run tests with profiling')
    args = parser.parse_args()

    if args.profile:
        success = profile_tests()
    else:
        success = run_tests()

    # Exit with appropriate status code
    sys.exit(not success)