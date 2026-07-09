from types import SimpleNamespace

from kispy.domestic_stock.order import OrderAPI


def make_order_api(is_real: bool = True) -> OrderAPI:
    auth = SimpleNamespace(
        is_real=is_real,
        cano="12345678",
        acnt_prdt_cd="01",
        get_header=lambda: {"authorization": "Bearer token", "appkey": "key", "appsecret": "secret"},
    )
    return OrderAPI(auth)


def test_prepare_nxt_cash_sell_order_uses_exchange_field_and_sell_tr_id():
    order = make_order_api().prepare_cash_order(
        stock_code="005930",
        side="sell",
        quantity=1,
        price=73000,
        exchange="NXT",
    )

    assert order.method == "post"
    assert order.path == "uapi/domestic-stock/v1/trading/order-cash"
    assert order.tr_id == "TTTC0011U"
    assert order.body == {
        "CANO": "12345678",
        "ACNT_PRDT_CD": "01",
        "PDNO": "005930",
        "ORD_DVSN": "00",
        "ORD_QTY": "1",
        "ORD_UNPR": "73000",
        "EXCG_ID_DVSN_CD": "NXT",
        "SLL_TYPE": "01",
        "CNDT_PRIC": "",
    }


def test_prepare_krx_preopen_cash_buy_order_uses_after_hours_close_code():
    order = make_order_api().prepare_cash_order(
        stock_code="005930",
        side="buy",
        quantity=1,
        price=0,
        exchange="KRX",
        order_type="05",
    )

    assert order.tr_id == "TTTC0012U"
    assert order.body["EXCG_ID_DVSN_CD"] == "KRX"
    assert order.body["ORD_DVSN"] == "05"
    assert order.body["ORD_UNPR"] == "0"
    assert order.body["SLL_TYPE"] == ""


def test_prepare_reservation_preopen_buy_order_uses_reservation_tr_id():
    order = make_order_api().prepare_reservation_order(
        stock_code="005930",
        side="buy",
        quantity=1,
        price=0,
        order_type="05",
    )

    assert order.path == "uapi/domestic-stock/v1/trading/order-resv"
    assert order.tr_id == "CTSC0008U"
    assert order.body == {
        "CANO": "12345678",
        "ACNT_PRDT_CD": "01",
        "PDNO": "005930",
        "ORD_QTY": "1",
        "ORD_UNPR": "0",
        "SLL_BUY_DVSN_CD": "02",
        "ORD_DVSN_CD": "05",
        "ORD_OBJT_CBLC_DVSN_CD": "10",
    }


def test_prepared_order_redacts_account_fields_for_dry_run_logs():
    order = make_order_api().prepare_cash_order(
        stock_code="005930",
        side="buy",
        quantity=1,
        price=0,
        order_type="05",
    )

    assert order.redacted_body() == {
        **order.body,
        "CANO": "***",
        "ACNT_PRDT_CD": "***",
    }


def test_buy_sends_prepared_order_and_preserves_full_response_shape(monkeypatch):
    api = make_order_api()
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(json={"rt_cd": "0", "output": {"ODNO": "0001"}})

    monkeypatch.setattr(api, "_request", fake_request)

    response = api.buy(stock_code="005930", quantity=1, price=0, exchange="KRX", order_type="05")

    assert response == {"rt_cd": "0", "output": {"ODNO": "0001"}}
    assert captured["method"] == "post"
    assert captured["headers"]["tr_id"] == "TTTC0012U"
    assert captured["json"]["ORD_DVSN"] == "05"
    assert captured["json"]["EXCG_ID_DVSN_CD"] == "KRX"
