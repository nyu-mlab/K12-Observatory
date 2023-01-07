"""Mocks the OpenTelemetry package if it's not installed
"""
import warnings

warnings.warn(
    "Cannot find OpenTelemetry packages, using mocks instead."
    "\n Install them with 'pip install -e .[\"trace\"]' if telemetry is needed")


class MockTrace:

    def __getattr__(self, name):

        def dummy(*args, **kwargs):
            return MockTrace()

        return dummy

    def __call__(self, *args, **kwargs):
        # Act as a decorator
        # to mock usages like "opentelemetry.tracer.start_as_current_span()"
        return args[0]


trace = MockTrace()
