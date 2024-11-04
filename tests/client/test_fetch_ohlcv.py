from datetime import datetime, timedelta

import pytest

from kispy.auth import KisAuth
from kispy.client import KisClientV2
from kispy.constants import Period


@pytest.mark.parametrize(
    "period, expected_length",
    [
        ("d", 250),
        ("w", 52),
        # ("M", 12),  # 월은 API 미지원
    ],
)
def test_fetch_ohlcv_various_daily_period(
    auth: KisAuth,
    period: Period,
    expected_length: int,
):
    client = KisClientV2(auth, "US")
    resp = client.fetch_ohlcv("AAPL", "2023-01-01", "2024-01-01", period)
    assert len(resp) == expected_length


@pytest.mark.parametrize(
    "period, expected_length",
    [
        ("1m", 391),
        ("3m", 131),
        ("5m", 79),
        ("10m", 40),
        ("15m", 27),
        ("30m", 14),
        ("1h", 7),
        ("2h", 4),
        ("4h", 2),
    ],
)
def test_fetch_ohlcv_various_minute_period(
    auth: KisAuth,
    period: Period,
    expected_length: int,
):
    client = KisClientV2(auth, "US")
    # 주말을 제외한 최근 하루의 분봉 시세 조회
    yesterday = datetime.now() - timedelta(days=1)
    while yesterday.weekday() >= 5:
        yesterday -= timedelta(days=1)
    resp = client.fetch_ohlcv(
        symbol="AAPL",
        start_date=(yesterday - timedelta(days=1)).strftime("%Y-%m-%d"),
        end_date=yesterday.strftime("%Y-%m-%d"),
        period=period,
    )
    assert len(resp) == expected_length
