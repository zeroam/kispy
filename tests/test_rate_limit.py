import time

from kispy.rate_limit import RateLimiter


def test_immediate_requests_within_limit():
    """Test that requests within rate limit are processed immediately."""
    limiter = RateLimiter()
    limiter.configure(max_requests=2, window=1.0)

    start = time.monotonic()
    limiter.wait_if_needed()  # First request
    limiter.wait_if_needed()  # Second request
    duration = time.monotonic() - start

    assert duration < 0.1, "Requests within limit should be immediate"


def test_wait_when_limit_exceeded():
    """Test that exceeding rate limit causes appropriate wait."""
    limiter = RateLimiter()
    limiter.configure(max_requests=2, window=1.0)

    start = time.monotonic()
    limiter.wait_if_needed()  # First request
    limiter.wait_if_needed()  # Second request
    limiter.wait_if_needed()  # Third request (should wait)
    duration = time.monotonic() - start

    assert duration >= 1.0, "Should wait when limit exceeded"


def test_sliding_window():
    """Test sliding window behavior."""
    limiter = RateLimiter()
    limiter.configure(max_requests=2, window=1.0)

    # Fill up the limit
    limiter.wait_if_needed()
    limiter.wait_if_needed()

    # Wait for half the window
    time.sleep(0.5)

    # Next request should wait for remaining half
    start = time.monotonic()
    limiter.wait_if_needed()
    duration = time.monotonic() - start

    assert 0.4 < duration < 0.6, "Should wait for remaining window time"


def test_performance():
    """Test that rate limiting doesn't cause significant overhead."""
    limiter = RateLimiter()
    limiter.configure(max_requests=10000, window=1.0)

    start = time.monotonic()
    for _ in range(10000):  # 파일 I/O가 없는 연속 요청
        limiter.wait_if_needed()
    duration = time.monotonic() - start

    assert duration < 0.1, "Processing 100 requests should be quick when within limits"


# TODO: 멀티프로세스 대응이 필요하면 추가
# def make_request():
#     limiter = RateLimiter()
#     limiter.configure(max_requests=5, window=1.0)
#     limiter.wait_if_needed()


# def test_multiprocess_rate_limiting():
#     """Test rate limiting across multiple processes."""
#     from multiprocessing import Process

#     # Start 10 processes (twice the rate limit)
#     processes = [Process(target=make_request) for _ in range(10)]
#     start = time.monotonic()

#     for p in processes:
#         p.start()

#     for p in processes:
#         p.join()

#     duration = time.monotonic() - start
#     assert duration >= 2.0, "Should take at least 2 seconds for 10 requests at 5 req/s"
