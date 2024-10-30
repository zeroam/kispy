from datetime import datetime, timedelta

from freezegun import freeze_time

from kispy.auth import KisAuth
from kispy.client import KisClient


@freeze_time("2024-01-03")
def test_get_stock_price_history(auth: KisAuth):
    quote = KisClient(auth).overseas_stock.quote
    start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    resp = quote.get_stock_price_history("AAPL", "NAS", start_date, end_date)

    assert len(resp) == 2


@freeze_time("2024-01-01")
def test_get_stock_price_history_with_empty(auth: KisAuth):
    quote = KisClient(auth).overseas_stock.quote
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    resp = quote.get_stock_price_history("AAPL", "NAS", yesterday, today)

    assert resp == []


@freeze_time("2024-01-03")
def test_get_stock_price_history_with_end_date_none(auth: KisAuth):
    quote = KisClient(auth).overseas_stock.quote
    resp = quote.get_stock_price_history("AAPL", "NAS", "2024-01-01", None)

    assert len(resp) == 2


@freeze_time("2024-01-03")
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
