from types import SimpleNamespace

import pytest

from kispy.exceptions import KispyException
from kispy.overseas_futures.order import OrderAPI


def make_order_api(is_real: bool = True) -> OrderAPI:
    auth = SimpleNamespace(
        is_real=is_real,
        cano="12345678",
        acnt_prdt_cd="01",
        get_header=lambda: {"authorization": "Bearer token", "appkey": "key", "appsecret": "secret"},
    )
    return OrderAPI(auth)


def test_prepare_overseas_futures_buy_order_uses_official_body_shape():
    order = make_order_api().prepare_order(
        symbol="MNQU24",
        side="buy",
        quantity=2,
        price="20000.25",
    )

    assert order.method == "post"
    assert order.path == "uapi/overseas-futureoption/v1/trading/order"
    assert order.tr_id == "OTFM3001U"
    assert order.body == {
        "CANO": "12345678",
        "ACNT_PRDT_CD": "01",
        "OVRS_FUTR_FX_PDNO": "MNQU24",
        "SLL_BUY_DVSN_CD": "02",
        "FM_LQD_USTL_CCLD_DT": "",
        "FM_LQD_USTL_CCNO": "",
        "PRIC_DVSN_CD": "1",
        "FM_LIMIT_ORD_PRIC": "20000.25",
        "FM_STOP_ORD_PRIC": "",
        "FM_ORD_QTY": "2",
        "FM_LQD_LMT_ORD_PRIC": "",
        "FM_LQD_STOP_ORD_PRIC": "",
        "CCLD_CNDT_CD": "6",
        "CPLX_ORD_DVSN_CD": "0",
        "ECIS_RSVN_ORD_YN": "N",
        "FM_HDGE_ORD_SCRN_YN": "N",
    }


def test_prepare_overseas_futures_sell_order_uses_sell_side_code():
    order = make_order_api().prepare_order(symbol="MNQU24", side="sell", quantity=1)

    assert order.body["SLL_BUY_DVSN_CD"] == "01"


def test_prepare_cancel_order_uses_cancel_tr_id_and_original_order_fields():
    order = make_order_api().prepare_cancel_order(
        order_number="0000000123",
        order_date="20260709",
        market_price_conversion="Y",
    )

    assert order.method == "post"
    assert order.path == "uapi/overseas-futureoption/v1/trading/order-rvsecncl"
    assert order.tr_id == "OTFM3003U"
    assert order.body == {
        "CANO": "12345678",
        "ACNT_PRDT_CD": "01",
        "ORGN_ORD_DT": "20260709",
        "ORGN_ODNO": "0000000123",
        "FM_LIMIT_ORD_PRIC": "",
        "FM_STOP_ORD_PRIC": "",
        "FM_LQD_LMT_ORD_PRIC": "",
        "FM_LQD_STOP_ORD_PRIC": "",
        "FM_HDGE_ORD_SCRN_YN": "N",
        "FM_MKPR_CVSN_YN": "Y",
    }


def test_prepared_order_redacts_account_fields_for_dry_run_logs():
    order = make_order_api().prepare_order(symbol="MNQU24", side="buy", quantity=1)

    assert order.redacted_body() == {
        **order.body,
        "CANO": "***",
        "ACNT_PRDT_CD": "***",
    }


def test_create_sends_prepared_order(monkeypatch):
    api = make_order_api()
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(json={"rt_cd": "0", "output": {"ODNO": "0001"}})

    monkeypatch.setattr(api, "_request", fake_request)

    response = api.create(symbol="MNQU24", side="buy", quantity=1)

    assert response == {"ODNO": "0001"}
    assert captured["method"] == "post"
    assert captured["headers"]["tr_id"] == "OTFM3001U"
    assert captured["json"]["OVRS_FUTR_FX_PDNO"] == "MNQU24"


def test_prepare_order_rejects_invalid_side():
    with pytest.raises(KispyException):
        make_order_api().prepare_order(symbol="MNQU24", side="hold", quantity=1)  # type: ignore[arg-type]
