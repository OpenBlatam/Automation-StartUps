#!/usr/bin/env python3
"""
ClickUp Brain Testing Framework
==============================

Comprehensive testing framework with fixtures, mocks, assertions,
and automated test discovery and execution.
"""

import asyncio
import unittest
import pytest
import time
import json
from typing import Any, Dict, List, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging
from abc import ABC, abstractmethod
from enum import Enum
import threading
from contextlib import asynccontextmanager
import inspect
import sys

ROOT = Path(__file__).parent

class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class TestLevel(Enum):
    """Test levels."""
    UNIT = "unit"
    INTEGRATION = "integration"
    SYSTEM = "system"
    E2E = "e2e"

@dataclass
class TestResult:
    """Test execution result."""
    test_name: str
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    assertions: int = 0
    passed_assertions: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestSuite:
    """Test suite configuration."""
    name: str
    level: TestLevel
    timeout: int = 300
    parallel: bool = False
    retry_count: int = 0
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

class TestAssertion:
    """Custom assertion class with detailed error messages."""
    
    def __init__(self, test_case):
        self.test_case = test_case
        self.assertions = 0
        self.passed_assertions = 0
    
    def assert_true(self, condition: bool, message: str = "Expected True") -> None:
        """Assert that condition is True."""
        self.assertions += 1
        if condition:
            self.passed_assertions += 1
        else:
            raise AssertionError(message)
    
    def assert_false(self, condition: bool, message: str = "Expected False") -> None:
        """Assert that condition is False."""
        self.assertions += 1
        if not condition:
            self.passed_assertions += 1
        else:
            raise AssertionError(message)
    
    def assert_equal(self, actual: Any, expected: Any, message: str = None) -> None:
        """Assert that actual equals expected."""
        self.assertions += 1
        if actual == expected:
            self.passed_assertions += 1
        else:
            if message is None:
                message = f"Expected {expected}, got {actual}"
            raise AssertionError(message)
    
    def assert_not_equal(self, actual: Any, expected: Any, message: str = None) -> None:
        """Assert that actual does not equal expected."""
        self.assertions += 1
        if actual != expected:
            self.passed_assertions += 1
        else:
            if message is None:
                message = f"Expected {actual} to not equal {expected}"
            raise AssertionError(message)
    
    def assert_in(self, item: Any, container: Any, message: str = None) -> None:
        """Assert that item is in container."""
        self.assertions += 1
        if item in container:
            self.passed_assertions += 1
        else:
            if message is None:
                message = f"Expected {item} to be in {container}"
            raise AssertionError(message)
    
    def assert_not_in(self, item: Any, container: Any, message: str = None) -> None:
        """Assert that item is not in container."""
        self.assertions += 1
        if item not in container:
            self.passed_assertions += 1
        else:
            if message is None:
                message = f"Expected {item} to not be in {container}"
            raise AssertionError(message)
    
    def assert_is_none(self, value: Any, message: str = "Expected None") -> None:
        """Assert that value is None."""
        self.assertions += 1
        if value is None:
            self.passed_assertions += 1
        else:
            raise AssertionError(message)
    
    def assert_is_not_none(self, value: Any, message: str = "Expected not None") -> None:
        """Assert that value is not None."""
        self.assertions += 1
        if value is not None:
            self.passed_assertions += 1
        else:
            raise AssertionError(message)
    
    def assert_raises(self, exception_class: Type[Exception], callable_obj: Callable, *args, **kwargs) -> Exception:
        """Assert that callable raises exception."""
        self.assertions += 1
        try:
            callable_obj(*args, **kwargs)
            raise AssertionError(f"Expected {exception_class.__name__} to be raised")
        except exception_class as e:
            self.passed_assertions += 1
            return e
        except Exception as e:
            raise AssertionError(f"Expected {exception_class.__name__}, got {type(e).__name__}: {e}")
    
    async def assert_async_raises(self, exception_class: Type[Exception], async_callable: Callable, *args, **kwargs) -> Exception:
        """Assert that async callable raises exception."""
        self.assertions += 1
        try:
            await async_callable(*args, **kwargs)
            raise AssertionError(f"Expected {exception_class.__name__} to be raised")
        except exception_class as e:
            self.passed_assertions += 1
            return e
        except Exception as e:
            raise AssertionError(f"Expected {exception_class.__name__}, got {type(e).__name__}: {e}")

class MockObject:
    """Mock object for testing."""
    
    def __init__(self, **kwargs):
        self._attributes = kwargs
        self._calls = []
        self._return_values = {}
        self._side_effects = {}
    
    def __getattr__(self, name: str) -> Any:
        if name in self._attributes:
            return self._attributes[name]
        
        # Create a mock method
        def mock_method(*args, **kwargs):
            call_info = {
                'method': name,
                'args': args,
                'kwargs': kwargs,
                'timestamp': datetime.now()
            }
            self._calls.append(call_info)
            
            # Check for side effects
            if name in self._side_effects:
                side_effect = self._side_effects[name]
                if callable(side_effect):
                    return side_effect(*args, **kwargs)
                else:
                    raise side_effect
            
            # Check for return values
            if name in self._return_values:
                return self._return_values[name]
            
            return MockObject()
        
        return mock_method
    
    def set_return_value(self, method_name: str, value: Any) -> None:
        """Set return value for a method."""
        self._return_values[method_name] = value
    
    def set_side_effect(self, method_name: str, side_effect: Union[Exception, Callable]) -> None:
        """Set side effect for a method."""
        self._side_effect[method_name] = side_effect
    
    def assert_called_with(self, method_name: str, *args, **kwargs) -> None:
        """Assert that method was called with specific arguments."""
        for call in self._calls:
            if (call['method'] == method_name and 
                call['args'] == args and 
                call['kwargs'] == kwargs):
                return
        
        raise AssertionError(f"Method {method_name} was not called with args {args} and kwargs {kwargs}")
    
    def assert_called(self, method_name: str) -> None:
        """Assert that method was called."""
        for call in self._calls:
            if call['method'] == method_name:
                return
        
        raise AssertionError(f"Method {method_name} was not called")
    
    def assert_not_called(self, method_name: str) -> None:
        """Assert that method was not called."""
        for call in self._calls:
            if call['method'] == method_name:
                raise AssertionError(f"Method {method_name} was called")
    
    def get_calls(self, method_name: str = None) -> List[Dict[str, Any]]:
        """Get all calls or calls for specific method."""
        if method_name:
            return [call for call in self._calls if call['method'] == method_name]
        return self._calls.copy()
    
    def reset(self) -> None:
        """Reset mock state."""
        self._calls.clear()
        self._return_values.clear()
        self._side_effects.clear()

class TestFixture:
    """Test fixture for setup and teardown."""
    
    def __init__(self, name: str):
        self.name = name
        self.setup_called = False
        self.teardown_called = False
        self.data = {}
    
    async def setup(self) -> None:
        """Setup fixture."""
        if not self.setup_called:
            await self._setup()
            self.setup_called = True
    
    async def teardown(self) -> None:
        """Teardown fixture."""
        if not self.teardown_called:
            await self._teardown()
            self.teardown_called = True
    
    async def _setup(self) -> None:
        """Override in subclasses."""
        pass
    
    async def _teardown(self) -> None:
        """Override in subclasses."""
        pass

class DatabaseFixture(TestFixture):
    """Database test fixture."""
    
    def __init__(self, name: str = "database"):
        super().__init__(name)
        self.db = None
        self.test_data = {}
    
    async def _setup(self) -> None:
        """Setup test database."""
        # Initialize test database
        from clickup_brain_database_orm import initialize_database, DatabaseConfig, DatabaseType
        
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            database=":memory:"  # In-memory database for tests
        )
        self.db = initialize_database(config)
        await self.db.initialize()
        
        # Create test tables
        await self._create_test_tables()
        
        # Insert test data
        await self._insert_test_data()
    
    async def _teardown(self) -> None:
        """Teardown test database."""
        if self.db:
            await self.db.close()
    
    async def _create_test_tables(self) -> None:
        """Create test tables."""
        # Override in subclasses
        pass
    
    async def _insert_test_data(self) -> None:
        """Insert test data."""
        # Override in subclasses
        pass

class CacheFixture(TestFixture):
    """Cache test fixture."""
    
    def __init__(self, name: str = "cache"):
        super().__init__(name)
        self.cache = None
    
    async def _setup(self) -> None:
        """Setup test cache."""
        from clickup_brain_caching import initialize_cache, CacheConfig
        
        config = CacheConfig(backend="memory", default_ttl=60)
        self.cache = initialize_cache(config)
    
    async def _teardown(self) -> None:
        """Teardown test cache."""
        if self.cache:
            await self.cache.clear()

class APIFixture(TestFixture):
    """API test fixture."""
    
    def __init__(self, name: str = "api"):
        super().__init__(name)
        self.client = None
        self.base_url = "http://localhost:8000"
    
    async def _setup(self) -> None:
        """Setup test API client."""
        import aiohttp
        
        self.client = aiohttp.ClientSession()
    
    async def _teardown(self) -> None:
        """Teardown test API client."""
        if self.client:
            await self.client.close()
    
    async def get(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """Make GET request."""
        url = f"{self.base_url}{path}"
        return await self.client.get(url, **kwargs)
    
    async def post(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """Make POST request."""
        url = f"{self.base_url}{path}"
        return await self.client.post(url, **kwargs)
    
    async def put(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """Make PUT request."""
        url = f"{self.base_url}{path}"
        return await self.client.put(url, **kwargs)
    
    async def delete(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """Make DELETE request."""
        url = f"{self.base_url}{path}"
        return await self.client.delete(url, **kwargs)

class TestCase:
    """Base test case class."""
    
    def __init__(self, test_name: str, test_method: Callable):
        self.test_name = test_name
        self.test_method = test_method
        self.fixtures: Dict[str, TestFixture] = {}
        self.assertions = TestAssertion(self)
        self.result: Optional[TestResult] = None
    
    def add_fixture(self, fixture: TestFixture) -> None:
        """Add fixture to test case."""
        self.fixtures[fixture.name] = fixture
    
    async def setup(self) -> None:
        """Setup test case."""
        for fixture in self.fixtures.values():
            await fixture.setup()
    
    async def teardown(self) -> None:
        """Teardown test case."""
        for fixture in self.fixtures.values():
            await fixture.teardown()
    
    async def run(self) -> TestResult:
        """Run test case."""
        start_time = time.time()
        self.result = TestResult(
            test_name=self.test_name,
            status=TestStatus.RUNNING,
            duration=0
        )
        
        try:
            # Setup
            await self.setup()
            
            # Run test
            if asyncio.iscoroutinefunction(self.test_method):
                await self.test_method(self)
            else:
                self.test_method(self)
            
            # Test passed
            self.result.status = TestStatus.PASSED
            self.result.assertions = self.assertions.assertions
            self.result.passed_assertions = self.assertions.passed_assertions
            
        except AssertionError as e:
            # Test failed
            self.result.status = TestStatus.FAILED
            self.result.error_message = str(e)
            self.result.assertions = self.assertions.assertions
            self.result.passed_assertions = self.assertions.passed_assertions
            
        except Exception as e:
            # Test error
            self.result.status = TestStatus.ERROR
            self.result.error_message = str(e)
            self.result.error_traceback = str(e.__traceback__)
            self.result.assertions = self.assertions.assertions
            self.result.passed_assertions = self.assertions.passed_assertions
            
        finally:
            # Teardown
            try:
                await self.teardown()
            except Exception as e:
                logging.error(f"Teardown error in {self.test_name}: {e}")
            
            # Calculate duration
            self.result.duration = time.time() - start_time
        
        return self.result

class TestRunner:
    """Test runner for executing test suites."""
    
    def __init__(self):
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_cases: Dict[str, List[TestCase]] = {}
        self.results: List[TestResult] = []
        self.logger = logging.getLogger("test_runner")
    
    def add_test_suite(self, suite: TestSuite) -> None:
        """Add test suite."""
        self.test_suites[suite.name] = suite
        self.test_cases[suite.name] = []
    
    def add_test_case(self, suite_name: str, test_case: TestCase) -> None:
        """Add test case to suite."""
        if suite_name not in self.test_cases:
            self.test_cases[suite_name] = []
        self.test_cases[suite_name].append(test_case)
    
    async def run_suite(self, suite_name: str) -> List[TestResult]:
        """Run a specific test suite."""
        if suite_name not in self.test_suites:
            raise ValueError(f"Test suite {suite_name} not found")
        
        suite = self.test_suites[suite_name]
        test_cases = self.test_cases.get(suite_name, [])
        
        self.logger.info(f"Running test suite: {suite_name}")
        
        results = []
        
        if suite.parallel:
            # Run tests in parallel
            tasks = []
            for test_case in test_cases:
                task = asyncio.create_task(test_case.run())
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_result = TestResult(
                        test_name=test_cases[i].test_name,
                        status=TestStatus.ERROR,
                        duration=0,
                        error_message=str(result)
                    )
                    results[i] = error_result
        else:
            # Run tests sequentially
            for test_case in test_cases:
                result = await test_case.run()
                results.append(result)
        
        self.results.extend(results)
        return results
    
    async def run_all(self) -> List[TestResult]:
        """Run all test suites."""
        all_results = []
        
        for suite_name in self.test_suites.keys():
            results = await self.run_suite(suite_name)
            all_results.extend(results)
        
        return all_results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test execution report."""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == TestStatus.PASSED])
        failed_tests = len([r for r in self.results if r.status == TestStatus.FAILED])
        error_tests = len([r for r in self.results if r.status == TestStatus.ERROR])
        skipped_tests = len([r for r in self.results if r.status == TestStatus.SKIPPED])
        
        total_duration = sum(r.duration for r in self.results)
        total_assertions = sum(r.assertions for r in self.results)
        passed_assertions = sum(r.passed_assertions for r in self.results)
        
        return {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'errors': error_tests,
                'skipped': skipped_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'total_duration': total_duration,
                'total_assertions': total_assertions,
                'passed_assertions': passed_assertions,
                'assertion_success_rate': (passed_assertions / total_assertions * 100) if total_assertions > 0 else 0
            },
            'results': [
                {
                    'test_name': r.test_name,
                    'status': r.status.value,
                    'duration': r.duration,
                    'error_message': r.error_message,
                    'assertions': r.assertions,
                    'passed_assertions': r.passed_assertions
                }
                for r in self.results
            ]
        }

# Decorators for test discovery
def test(level: TestLevel = TestLevel.UNIT, tags: List[str] = None, timeout: int = 300):
    """Decorator for marking test methods."""
    def decorator(func: Callable) -> Callable:
        func._test_level = level
        func._test_tags = tags or []
        func._test_timeout = timeout
        return func
    return decorator

def fixture(name: str = None):
    """Decorator for marking fixture methods."""
    def decorator(func: Callable) -> Callable:
        func._fixture_name = name or func.__name__
        return func
    return decorator

def skip(reason: str = "No reason provided"):
    """Decorator for skipping tests."""
    def decorator(func: Callable) -> Callable:
        func._skip = True
        func._skip_reason = reason
        return func
    return decorator

# Global test runner
test_runner = TestRunner()

def discover_tests(test_dir: Path = None) -> None:
    """Discover and register tests from directory."""
    if test_dir is None:
        test_dir = ROOT / "tests"
    
    if not test_dir.exists():
        return
    
    for test_file in test_dir.glob("test_*.py"):
        # Import test module
        module_name = test_file.stem
        spec = importlib.util.spec_from_file_location(module_name, test_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find test classes and methods
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and hasattr(obj, '_test_suite'):
                suite = obj._test_suite
                test_runner.add_test_suite(suite)
                
                # Find test methods
                for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                    if hasattr(method, '_test_level'):
                        test_case = TestCase(f"{obj.__name__}.{method_name}", method)
                        test_runner.add_test_case(suite.name, test_case)

if __name__ == "__main__":
    # Demo testing framework
    print("ClickUp Brain Testing Framework Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        # Create test suite
        suite = TestSuite("demo_suite", TestLevel.UNIT)
        test_runner.add_test_suite(suite)
        
        # Create test cases
        @test(TestLevel.UNIT)
        async def test_basic_assertions(test_case):
            test_case.assertions.assert_equal(1 + 1, 2)
            test_case.assertions.assert_true(True)
            test_case.assertions.assert_false(False)
            test_case.assertions.assert_in("hello", "hello world")
        
        @test(TestLevel.UNIT)
        async def test_mock_object(test_case):
            mock = MockObject()
            mock.set_return_value("get_data", {"key": "value"})
            
            result = mock.get_data()
            test_case.assertions.assert_equal(result, {"key": "value"})
            mock.assert_called("get_data")
        
        @test(TestLevel.INTEGRATION)
        async def test_with_fixtures(test_case):
            # Add fixtures
            cache_fixture = CacheFixture()
            test_case.add_fixture(cache_fixture)
            
            # Test with cache
            await test_case.setup()
            test_case.assertions.assert_is_not_none(cache_fixture.cache)
            await test_case.teardown()
        
        # Add test cases to suite
        test_runner.add_test_case("demo_suite", TestCase("test_basic_assertions", test_basic_assertions))
        test_runner.add_test_case("demo_suite", TestCase("test_mock_object", test_mock_object))
        test_runner.add_test_case("demo_suite", TestCase("test_with_fixtures", test_with_fixtures))
        
        # Run tests
        results = await test_runner.run_suite("demo_suite")
        
        # Generate report
        report = test_runner.generate_report()
        print(f"Test Report: {json.dumps(report, indent=2)}")
        
        print("\nTesting framework demo completed!")
    
    asyncio.run(demo())









