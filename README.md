# Requirements

Write a test suite for each of two different Python programs using test doubles (mocks, stubs, and fakes). For both test suites, use pytest, pytest-describe, and pytest-spec to implement your test cases, and use pytest-mock as a wrapper for Python's unittest.mock mock object library.

- For the first test suite, use test doubles to test each of the four methods within the provided MyDB class. Assume the implementations of the MyDB methods are correct.
	- Stubs should be used appropriately to prevent external dependencies (os and pickle) from being invoked during execution of the test suite.

	- Mocks should be used to appropriately assert that stubbed methods have been invoked correctly.

- For the second test suite, you will use test doubles to test each of the six handle___ methods within the provided SquirrelServerHandler class. Assume the implementations of the SquirrelServerHandler methods are correct.

	- As above, stubs should be used to prevent execution of external dependencies, and mocks should be used to assert that stubbed methods have been invoked correctly.

	- All integrations with SquirrelDB methods and BaseHTTPRequestHandler methods should be tested. Do not test these directly; rather, test their dependents using test doubles. The getRequestData and parsePath methods should not be considered integrations and need not be stubbed nor tested directly (they will be tested indirectly through other test cases).

	- Use the provided FakeRequest class and the example fixtures and test cases to get started.

	- All conditional branches within each method should be tested. For example, be sure to test all occurrences of handle404.

	- Since stubs will be used for all integrations, the HTTPServer class (and the run function) should not be instantiated, invoked or tested.

- Continue using describe blocks to appropriately describe components (classes, methods, etc.). Thoroughly and intentionally plan and design your test cases to achieve full test coverage of the test subjects. Try to maximize the number of test cases and minimize the number of assertions in each test case.

- Your submission will be evaluated according to the quality, variety, coverage, and intentional design of your test cases. You must implement all test cases using test doubles, and you will be graded according to your methodical and correct usage of each type of double.
