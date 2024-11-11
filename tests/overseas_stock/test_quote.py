from datetime import datetime, timedelta

from freezegun import freeze_time

from kispy.auth import KisAuth
from kispy.client import KisClient


def test_get_stock_price_history(auth: KisAuth):
    quote = KisClient(auth).overseas_stock.quote
    start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = "2024-01-01"
    end_date = "2024-01-03"
    resp = quote.get_stock_price_history("AAPL", "NAS", start_date, end_date)

    assert len(resp) == 2


def test_get_stock_price_history_with_empty(auth: KisAuth):
    quote = KisClient(auth).overseas_stock.quote
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday = "2024-12-31"
    today = "2024-01-01"
    resp = quote.get_stock_price_history("AAPL", "NAS", yesterday, today)

    assert resp == []


@freeze_time("2024-01-03", tz_offset=5)
def test_get_stock_price_history_with_end_date_none(auth: KisAuth):
    quote = KisClient(auth).overseas_stock.quote
    resp = quote.get_stock_price_history("AAPL", "NAS", "2024-01-01", None)

    assert len(resp) == 2


@freeze_time("2024-01-03", tz_offset=5)
def test_get_stock_price_history_with_end_date_future(auth: KisAuth):
    quote = KisClient(auth).overseas_stock.quote
    today = datetime.now().strftime("%Y-%m-%d")
    future = datetime(2099, 1, 1).strftime("%Y-%m-%d")
    resp = quote.get_stock_price_history("AAPL", "NAS", today, future)

    assert len(resp) == 1


def test_get_stock_price_history_with_not_exists_in_start_date(auth: KisAuth):
    quote = KisClient(auth).overseas_stock.quote
    # 20070820 ~ 20070831
    resp = quote.get_stock_price_history("AAPL", "NAS", "1960-01-01", "2007-09-01")

    assert len(resp) == 10
    assert resp[0]["xymd"] == "20070820"


def test_get_stock_price_history_with_asc(auth: KisAuth):
    quote = KisClient(auth).overseas_stock.quote
    # 20070820 ~ 20070831
    resp = quote.get_stock_price_history("AAPL", "NAS", "1960-01-01", "2007-09-01", desc=True)

    assert len(resp) == 10
    assert resp[0]["xymd"] == "20070831"


def test_get_stock_price_history_with_limit(auth: KisAuth):
    quote = KisClient(auth).overseas_stock.quote
    resp = quote.get_stock_price_history("AAPL", "NAS", limit=5)

    assert len(resp) == 5


def test_get_stock_price_history_by_minute(auth: KisAuth):
    quote = KisClient(auth).overseas_stock.quote
    # 주말을 제외한 최근 하루의 분봉 시세 조회
    yesterday = datetime.now() - timedelta(days=1)
    while yesterday.weekday() >= 5:
        yesterday -= timedelta(days=1)

    resp = quote.get_stock_price_history_by_minute(
        symbol="AAPL",
        exchange_code="NAS",
        start_date=(yesterday - timedelta(days=1)).strftime("%Y-%m-%d"),
        end_date=yesterday.strftime("%Y-%m-%d"),
        period="1",
        limit=None,
    )

    assert len(resp) == 391


def test_get_stock_price_history_by_minute_with_limit(auth: KisAuth):
    quote = KisClient(auth).overseas_stock.quote
    yesterday = datetime.now() - timedelta(days=1)
    while yesterday.weekday() >= 5:
        yesterday -= timedelta(days=1)

    resp = quote.get_stock_price_history_by_minute(
        symbol="AAPL",
        exchange_code="NAS",
        start_date=(yesterday - timedelta(days=1)).strftime("%Y-%m-%d"),
        end_date=yesterday.strftime("%Y-%m-%d"),
        limit=10,
    )

    assert len(resp) == 10


def test_get_stock_price_history_by_minute_not_exists(auth: KisAuth):
    quote = KisClient(auth).overseas_stock.quote
    resp = quote.get_stock_price_history_by_minute(
        symbol="AAPL",
        exchange_code="NAS",
        start_date="2024-11-01",
        end_date="2024-11-02",
        limit=10,
    )

    assert resp == []
