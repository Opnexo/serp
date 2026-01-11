"""Tests for retry pattern."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from serp_core.resilience import RetryPolicy, retry_with_backoff


class TestRetryPolicy:
    """Test RetryPolicy class."""

    def test_default_values(self):
        """Test default configuration values."""
        policy = RetryPolicy()

        assert policy.max_retries == 3
        assert policy.base_delay == 1.0
        assert policy.max_delay == 60.0
        assert policy.exponential_base == 2.0
        assert policy.jitter == 0.1

    def test_calculate_delay_exponential(self):
        """Test exponential backoff calculation."""
        policy = RetryPolicy(
            base_delay=1.0,
            exponential_base=2.0,
            jitter=0.0,  # No jitter for predictable testing
        )

        assert policy.calculate_delay(0) == 1.0   # 1 * 2^0
        assert policy.calculate_delay(1) == 2.0   # 1 * 2^1
        assert policy.calculate_delay(2) == 4.0   # 1 * 2^2
        assert policy.calculate_delay(3) == 8.0   # 1 * 2^3

    def test_calculate_delay_max_cap(self):
        """Test that delay is capped at max_delay."""
        policy = RetryPolicy(
            base_delay=1.0,
            max_delay=5.0,
            exponential_base=2.0,
            jitter=0.0,
        )

        # 1 * 2^10 = 1024, but should be capped at 5
        assert policy.calculate_delay(10) == 5.0

    def test_calculate_delay_with_jitter(self):
        """Test that jitter adds variance to delay."""
        policy = RetryPolicy(
            base_delay=10.0,
            jitter=0.5,  # 50% jitter
        )

        delays = [policy.calculate_delay(0) for _ in range(100)]

        # All should be within jitter range (5-15 for base=10, jitter=0.5)
        assert all(5.0 <= d <= 15.0 for d in delays)

        # Should have variance (not all the same)
        assert len(set(delays)) > 1

    def test_should_retry_within_max(self):
        """Test should_retry within max retries."""
        policy = RetryPolicy(max_retries=3)

        assert policy.should_retry(Exception(), attempt=0)
        assert policy.should_retry(Exception(), attempt=1)
        assert policy.should_retry(Exception(), attempt=2)
        assert not policy.should_retry(Exception(), attempt=3)

    def test_should_retry_retryable_exceptions(self):
        """Test should_retry with specific exception types."""
        policy = RetryPolicy(
            max_retries=3,
            retryable_exceptions=(ConnectionError, TimeoutError),
        )

        assert policy.should_retry(ConnectionError(), attempt=0)
        assert policy.should_retry(TimeoutError(), attempt=0)
        assert not policy.should_retry(ValueError(), attempt=0)

    def test_should_retry_non_retryable_exceptions(self):
        """Test should_retry excludes non-retryable exceptions."""
        policy = RetryPolicy(
            max_retries=3,
            retryable_exceptions=(Exception,),
            non_retryable_exceptions=(ValueError, KeyError),
        )

        assert policy.should_retry(RuntimeError(), attempt=0)
        assert not policy.should_retry(ValueError(), attempt=0)
        assert not policy.should_retry(KeyError(), attempt=0)


@pytest.mark.asyncio
class TestRetryPolicyAsync:
    """Test RetryPolicy async execution."""

    async def test_execute_success(self):
        """Test successful execution."""
        policy = RetryPolicy()
        mock_func = AsyncMock(return_value="result")

        result = await policy.execute(mock_func)

        assert result == "result"
        assert mock_func.call_count == 1

    async def test_execute_retry_then_success(self):
        """Test retry followed by success."""
        policy = RetryPolicy(
            max_retries=3,
            base_delay=0.01,
        )

        call_count = 0

        async def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("temporary failure")
            return "success"

        result = await policy.execute(flaky_function)

        assert result == "success"
        assert call_count == 3

    async def test_execute_all_retries_fail(self):
        """Test that exception is raised after all retries fail."""
        policy = RetryPolicy(
            max_retries=2,
            base_delay=0.01,
        )

        async def always_fails():
            raise ConnectionError("permanent failure")

        with pytest.raises(ConnectionError):
            await policy.execute(always_fails)

    async def test_execute_non_retryable_fails_immediately(self):
        """Test that non-retryable exceptions fail immediately."""
        policy = RetryPolicy(
            max_retries=3,
            base_delay=0.01,
            non_retryable_exceptions=(ValueError,),
        )

        call_count = 0

        async def fail_with_value_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("not retryable")

        with pytest.raises(ValueError):
            await policy.execute(fail_with_value_error)

        # Should have failed on first attempt
        assert call_count == 1

    async def test_execute_passes_args(self):
        """Test that arguments are passed to function."""
        policy = RetryPolicy()

        async def func_with_args(a, b, c=None):
            return (a, b, c)

        result = await policy.execute(func_with_args, 1, 2, c=3)

        assert result == (1, 2, 3)


@pytest.mark.asyncio
class TestRetryWithBackoffDecorator:
    """Test retry_with_backoff decorator."""

    async def test_decorator_success(self):
        """Test decorator on successful function."""
        @retry_with_backoff(max_retries=3)
        async def successful():
            return "result"

        result = await successful()
        assert result == "result"

    async def test_decorator_retry_then_success(self):
        """Test decorator retries then succeeds."""
        attempt = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        async def flaky():
            nonlocal attempt
            attempt += 1
            if attempt < 2:
                raise ConnectionError()
            return "success"

        result = await flaky()

        assert result == "success"
        assert attempt == 2

    async def test_decorator_with_custom_exceptions(self):
        """Test decorator with custom retryable exceptions."""
        attempt = 0

        @retry_with_backoff(
            max_retries=3,
            base_delay=0.01,
            retryable_exceptions=(ConnectionError,),
        )
        async def specific_retry():
            nonlocal attempt
            attempt += 1
            if attempt == 1:
                raise ConnectionError()
            if attempt == 2:
                raise ValueError()  # Not retryable
            return "never reached"

        with pytest.raises(ValueError):
            await specific_retry()

        assert attempt == 2
