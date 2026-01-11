"""Tests for timeout utilities."""

import asyncio

import pytest

from serp_core.resilience import TimeoutError, with_timeout


class TestTimeoutError:
    """Test TimeoutError exception."""

    def test_basic_error(self):
        """Test basic TimeoutError creation."""
        error = TimeoutError(timeout=5.0)

        assert error.timeout == 5.0
        assert error.operation is None

    def test_error_with_operation(self):
        """Test TimeoutError with operation name."""
        error = TimeoutError(timeout=5.0, operation="fetch_data")

        assert error.timeout == 5.0
        assert error.operation == "fetch_data"
        assert "fetch_data" in str(error)
        assert "5" in str(error)

    def test_error_with_custom_message(self):
        """Test TimeoutError with custom message."""
        error = TimeoutError(
            timeout=5.0,
            operation="custom_op",
            message="Custom timeout message"
        )

        assert str(error) == "Custom timeout message"


@pytest.mark.asyncio
class TestWithTimeout:
    """Test with_timeout function and decorator."""

    async def test_completes_within_timeout(self):
        """Test operation that completes within timeout."""
        @with_timeout(1.0)
        async def fast_operation():
            await asyncio.sleep(0.01)
            return "result"

        result = await fast_operation()
        assert result == "result"

    async def test_exceeds_timeout(self):
        """Test operation that exceeds timeout."""
        @with_timeout(0.01)
        async def slow_operation():
            await asyncio.sleep(1.0)
            return "never reached"

        with pytest.raises(TimeoutError) as exc_info:
            await slow_operation()

        assert exc_info.value.timeout == 0.01
        assert exc_info.value.operation == "slow_operation"

    async def test_with_custom_operation_name(self):
        """Test decorator with custom operation name."""
        @with_timeout(0.01, operation_name="my_custom_operation")
        async def slow_operation():
            await asyncio.sleep(1.0)

        with pytest.raises(TimeoutError) as exc_info:
            await slow_operation()

        assert exc_info.value.operation == "my_custom_operation"

    async def test_passes_arguments(self):
        """Test that arguments are passed correctly."""
        @with_timeout(1.0)
        async def func_with_args(a, b, c=None):
            return (a, b, c)

        result = await func_with_args(1, 2, c=3)
        assert result == (1, 2, 3)

    async def test_preserves_exception(self):
        """Test that non-timeout exceptions are preserved."""
        @with_timeout(1.0)
        async def raises_value_error():
            raise ValueError("original error")

        with pytest.raises(ValueError, match="original error"):
            await raises_value_error()
