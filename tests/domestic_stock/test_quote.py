from datetime import datetime, timedelta

from freezegun import freeze_time

from kispy.auth import KisAuth
from kispy.client import KisClient


@freeze_time("2024-01-03")
def test_get_stock_price_history(auth: KisAuth):
    quote = KisClient(auth).domestic_stock.quote
    start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    resp = quote.get_stock_price_history("005930", start_date, end_date)

    assert len(resp) == 2


@freeze_time("2024-01-01")
def test_get_stock_price_history_with_empty(auth: KisAuth):
    quote = KisClient(auth).domestic_stock.quote
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    resp = quote.get_stock_price_history("005930", yesterday, today)

    assert resp == []


@freeze_time("2024-01-03")
def test_get_stock_price_history_with_end_date_none(auth: KisAuth):
    quote = KisClient(auth).domestic_stock.quote
    resp = quote.get_stock_price_history("005930", "2024-01-01", None)

    assert len(resp) == 2


@freeze_time("2024-01-03")
def test_get_stock_price_history_with_end_date_future(auth: KisAuth):
    quote = KisClient(auth).domestic_stock.quote
    today = datetime.now().strftime("%Y-%m-%d")
    future = datetime(2099, 1, 1).strftime("%Y-%m-%d")
    resp = quote.get_stock_price_history("005930", today, future)

    assert len(resp) == 1


def test_get_stock_price_history_with_not_exists_in_start_date(auth: KisAuth):
    quote = KisClient(auth).domestic_stock.quote
    resp = quote.get_stock_price_history("005930", "1960-01-01", "1985-01-05")

    assert len(resp) == 2


def test_get_stock_price_history_by_minute(auth: KisAuth):
    """
    현재 시각부터 조회 (기본 120건)
    """
    quote = KisClient(auth).domestic_stock.quote
    resp = quote.get_stock_price_history_by_minute(
        stock_code="005930",
    )

    assert len(resp) <= 120
    if len(resp) > 1:
        # 기본적으로 과거순 정렬 (오름차순)
        first_time = int(resp[0]["stck_cntg_hour"])
        last_time = int(resp[-1]["stck_cntg_hour"])
        assert first_time < last_time


def test_get_stock_price_history_by_minute_with_limit(auth: KisAuth):
    """
    limit 파라미터 테스트
    """
    quote = KisClient(auth).domestic_stock.quote
    resp = quote.get_stock_price_history_by_minute(
        stock_code="005930",
        limit=50,
    )

    assert len(resp) <= 50


def test_get_stock_price_history_by_minute_with_desc(auth: KisAuth):
    """
    desc 파라미터 테스트 (시간 역순 정렬)
    """
    quote = KisClient(auth).domestic_stock.quote
    resp = quote.get_stock_price_history_by_minute(
        stock_code="005930",
        desc=True,
    )

    if len(resp) > 1:
        # 시간 역순 정렬 (내림차순)
        first_time = int(resp[0]["stck_cntg_hour"])
        last_time = int(resp[-1]["stck_cntg_hour"])
        assert first_time > last_time


def test_get_stock_price_history_by_minute_with_specific_time(auth: KisAuth):
    """
    오전 10시부터 조회
    """
    quote = KisClient(auth).domestic_stock.quote 
    resp = quote.get_stock_price_history_by_minute(
        stock_code="005930",
        time="100000",
    )

    assert len(resp) <= 120
    if resp:
        # 10시 이후의 데이터가 포함되어 있어야 함
        last_time = int(resp[-1]["stck_cntg_hour"])
        assert last_time >= 100000


def test_get_stock_price_history_by_minute_with_include_hour(auth: KisAuth):
    """
    시간외 거래 포함하여 조회
    """
    quote = KisClient(auth).domestic_stock.quote
    resp = quote.get_stock_price_history_by_minute(
        stock_code="005930",
        include_hour=True,
    )

    assert len(resp) <= 120


def test_get_stock_price_history_by_minute_with_future_time(auth: KisAuth):
    """
    미래 시각 입력 시 현재 시각으로 조회됨
    """
    quote = KisClient(auth).domestic_stock.quote
    current_hour = datetime.now().strftime("%H")
    future_time = f"{int(current_hour)+1:02d}0000"  # 현재보다 1시간 뒤
    
    resp = quote.get_stock_price_history_by_minute(
        stock_code="005930",
        time=future_time,
    )

    assert len(resp) <= 120
    if resp:
        last_time = int(resp[-1]["stck_cntg_hour"])
        assert last_time <= int(future_time)


def test_get_stock_price_history_by_minute_not_exists(auth: KisAuth):
    """
    장 시작 전 시간으로 조회 시 데이터가 없어야 함
    """
    quote = KisClient(auth).domestic_stock.quote
    resp = quote.get_stock_price_history_by_minute(
        stock_code="005930",
        time="040000",  # 새벽 4시
    )

    assert resp == []
