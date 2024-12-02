import unittest
import sys
import os
import coverage
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from colorama import init, Fore, Style
from flask_migrate import upgrade
from tests.test_commands import TestCommands
import argparse

# Initialize colorama for cross-platform colored output
init()

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@dataclass
class TestMetrics:
    """Store metrics for a test run"""
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    total_time: float = 0.0

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = Fore.CYAN
    PASS = Fore.GREEN
    FAIL = Fore.RED
    SKIP = Fore.YELLOW
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT

# Initialize coverage reporting with more specific settings
COV = coverage.Coverage(
    branch=True,
    include='app/*',
    omit=[
        'app/templates/*',
        'tests/*',
        '*/migrations/*',
        'app/static/*',
        'app/__init__.py'
    ],
    source=['app']
)
COV.start()

from app import create_app, db
from app.models import User, Post, Comment, SiteSettings

class TestDatabaseManager:
    """Manage test database operations"""
    def __init__(self, app):
        self.app = app
        self.test_data_created = False

    def init_db(self) -> None:
        """Initialize the test database"""
        with self.app.app_context():
            db.create_all()

    def cleanup_db(self) -> None:
        """Clean up the test database"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def reset_db(self) -> None:
        """Reset the test database to a clean state"""
        self.cleanup_db()
        self.init_db()

    def create_test_data(self) -> None:
        """Create initial test data if not already created"""
        if self.test_data_created:
            return

        with self.app.app_context():
            # Create test data (your existing create_test_data implementation)
            # ... [previous implementation remains the same]
            self.test_data_created = True

class EnhancedTestResult(unittest.TestResult):
    """Enhanced test result collector with timing and categorization"""
    def __init__(self):
        super().__init__()
        self.start_time: float = 0.0
        self.test_results: List[Tuple] = []
        self.current_category: Optional[str] = None
        self.metrics = TestMetrics()

    def startTest(self, test) -> None:
        self.start_time = time.time()
        super().startTest(test)

    def addSuccess(self, test) -> None:
        self._record_result(test, "PASS")
        self.metrics.passed += 1

    def addError(self, test, err) -> None:
        self._record_result(test, "ERROR", err)
        self.metrics.errors += 1

    def addFailure(self, test, err) -> None:
        self._record_result(test, "FAIL", err)
        self.metrics.failed += 1

    def addSkip(self, test, reason) -> None:
        self._record_result(test, "SKIP", reason)
        self.metrics.skipped += 1

    def _record_result(self, test, status, error=None) -> None:
        elapsed_time = time.time() - self.start_time
        self.test_results.append((
            test.__class__.__name__,
            test._testMethodName,
            status,
            elapsed_time,
            error,
            test._testMethodDoc
        ))
        self.metrics.total_time += elapsed_time

class EnhancedTestRunner(unittest.TextTestRunner):
    """Enhanced test runner with improved output formatting"""
    def __init__(self):
        super().__init__(resultclass=EnhancedTestResult)

    def run(self, test) -> EnhancedTestResult:
        """Run tests with enhanced output formatting"""
        self._print_header("React Blog Test Suite")
        
        result = EnhancedTestResult()
        start_time = time.time()
        test(result)
        
        # Group and print results by category
        self._print_results_by_category(result)
        
        # Print summary
        self._print_summary(result, time.time() - start_time)
        
        return result

    def _print_header(self, title: str) -> None:
        """Print a formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
        print(f"{title.center(80)}")
        print(f"{'='*80}{Colors.RESET}\n")

    def _print_results_by_category(self, result: EnhancedTestResult) -> None:
        """Print test results grouped by category"""
        categories: Dict[str, List] = {}
        for test_result in result.test_results:
            category = test_result[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(test_result)

        for category, tests in sorted(categories.items()):
            print(f"\n{Colors.BOLD}{category}:{Colors.RESET}")
            print("-" * 80)
            
            for _, method, status, time, error, doc in tests:
                status_color = {
                    "PASS": Colors.PASS,
                    "FAIL": Colors.FAIL,
                    "ERROR": Colors.FAIL,
                    "SKIP": Colors.SKIP
                }.get(status, "")
                
                status_symbol = "✓" if status == "PASS" else "✗"
                print(f"{status_color}{status_symbol} {method:<50} {time:>6.2f}s{Colors.RESET}")
                
                if doc:
                    print(f"   {Colors.HEADER}{doc.strip()}{Colors.RESET}")
                if error:
                    print(f"   {Colors.FAIL}Error: {str(error)}{Colors.RESET}")

    def _print_summary(self, result: EnhancedTestResult, total_time: float) -> None:
        """Print test execution summary"""
        self._print_header("Test Summary")
        
        metrics = [
            ("Total tests", result.metrics.passed + result.metrics.failed + result.metrics.errors),
            ("Passed", result.metrics.passed, Colors.PASS),
            ("Failed", result.metrics.failed, Colors.FAIL),
            ("Errors", result.metrics.errors, Colors.FAIL),
            ("Skipped", result.metrics.skipped, Colors.SKIP),
            ("Total time", f"{total_time:.2f}s")
        ]

        for metric in metrics:
            if len(metric) == 3:
                name, value, color = metric
                print(f"{name:<15}: {color}{value}{Colors.RESET}")
            else:
                name, value = metric
                print(f"{name:<15}: {value}")

def setup_test_environment():
    """Set up the test environment"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.localdomain'
    })
    return app, TestDatabaseManager(app)

def run_tests():
    """Run the test suite with enhanced output"""
    app, db_manager = setup_test_environment()

    try:
        db_manager.init_db()
        
        # Discover and run tests
        loader = unittest.TestLoader()
        loader.sortTestMethodsUsing = None  # Preserve test order
        tests = loader.discover('tests', pattern='test_*.py')
        
        # Run tests with enhanced runner
        runner = EnhancedTestRunner()
        result = runner.run(tests)

        if COV:
            _generate_coverage_report()

        return result.wasSuccessful()

    finally:
        db_manager.cleanup_db()

def _generate_coverage_report():
    """Generate and print coverage report"""
    COV.stop()
    COV.save()
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
    print("Coverage Report".center(80))
    print(f"{'='*80}{Colors.RESET}\n")
    
    COV.report()
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, 'coverage')
    COV.html_report(directory=covdir)
    print(f'\n{Colors.BOLD}Detailed HTML coverage report: '
          f'{Colors.HEADER}file://{covdir}/index.html{Colors.RESET}')

def profile_tests():
    """Run tests with profiling enabled"""
    import cProfile
    import pstats
    from pstats import SortKey
    
    profiler = cProfile.Profile()
    profiler.enable()
    success = run_tests()
    profiler.disable()
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
    print("Performance Profile".center(80))
    print(f"{'='*80}{Colors.RESET}\n")
    
    stats = pstats.Stats(profiler).sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(30)  # Show top 30 time-consuming operations
    
    return success

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the React Blog test suite')
    parser.add_argument('--coverage', action='store_true', 
                       help='Run tests with coverage reporting')
    parser.add_argument('--profile', action='store_true', 
                       help='Run tests with profiling')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show verbose output')
    args = parser.parse_args()

    try:
        success = profile_tests() if args.profile else run_tests()
        sys.exit(not success)
    except KeyboardInterrupt:
        print(f"\n{Colors.FAIL}Test run interrupted by user{Colors.RESET}")
        sys.exit(1)