from types import SimpleNamespace

from kispy.domestic_stock.quote import QuoteAPI
from kispy.domestic_stock.realtime import RealtimeAPI


def make_quote_api() -> QuoteAPI:
    auth = SimpleNamespace(
        is_real=True,
        get_header=lambda: {"authorization": "Bearer token", "appkey": "key", "appsecret": "secret"},
    )
    return QuoteAPI(auth)


def test_prepare_overtime_asking_price_request_matches_official_sample():
    request = make_quote_api().prepare_overtime_asking_price("005930")

    assert request.method == "get"
    assert request.path == "uapi/domestic-stock/v1/quotations/inquire-overtime-asking-price"
    assert request.tr_id == "FHPST02300400"
    assert request.params == {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": "005930",
    }


def test_get_overtime_asking_price_sends_prepared_request(monkeypatch):
    api = make_quote_api()
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(json={"output": {"ovtm_askp1": "73000"}})

    monkeypatch.setattr(api, "_request", fake_request)

    response = api.get_overtime_asking_price("005930")

    assert response == {"ovtm_askp1": "73000"}
    assert captured["method"] == "get"
    assert captured["headers"]["tr_id"] == "FHPST02300400"
    assert captured["params"]["FID_INPUT_ISCD"] == "005930"


def test_prepare_after_hour_balance_request_defaults_to_preopen_rank():
    request = make_quote_api().prepare_after_hour_balance()

    assert request.method == "get"
    assert request.path == "uapi/domestic-stock/v1/ranking/after-hour-balance"
    assert request.tr_id == "FHPST01760000"
    assert request.params == {
        "fid_input_price_1": "",
        "fid_cond_mrkt_div_code": "J",
        "fid_cond_scr_div_code": "20176",
        "fid_rank_sort_cls_code": "1",
        "fid_div_cls_code": "0",
        "fid_input_iscd": "0000",
        "fid_trgt_exls_cls_code": "0",
        "fid_trgt_cls_code": "0",
        "fid_vol_cnt": "",
        "fid_input_price_2": "",
    }


def test_get_after_hour_balance_sends_preopen_rank_request(monkeypatch):
    api = make_quote_api()
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(json={"output": [{"hts_kor_isnm": "삼성전자"}]})

    monkeypatch.setattr(api, "_request", fake_request)

    response = api.get_after_hour_balance()

    assert response == [{"hts_kor_isnm": "삼성전자"}]
    assert captured["headers"]["tr_id"] == "FHPST01760000"
    assert captured["params"]["fid_rank_sort_cls_code"] == "1"


def test_prepare_time_overtime_conclusion_request_matches_official_sample():
    request = make_quote_api().prepare_time_overtime_conclusion("005930")

    assert request.method == "get"
    assert request.path == "uapi/domestic-stock/v1/quotations/inquire-time-overtimeconclusion"
    assert request.tr_id == "FHPST02310000"
    assert request.params == {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": "005930",
        "FID_HOUR_CLS_CODE": "1",
    }


def test_get_time_overtime_conclusion_preserves_summary_and_rows(monkeypatch):
    api = make_quote_api()
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            json={
                "output1": {"stck_shrn_iscd": "005930"},
                "output2": [{"stck_cntg_hour": "083000", "stck_prpr": "73000"}],
            }
        )

    monkeypatch.setattr(api, "_request", fake_request)

    response = api.get_time_overtime_conclusion("005930")

    assert response == {
        "output1": {"stck_shrn_iscd": "005930"},
        "output2": [{"stck_cntg_hour": "083000", "stck_prpr": "73000"}],
    }
    assert captured["method"] == "get"
    assert captured["headers"]["tr_id"] == "FHPST02310000"
    assert captured["params"]["FID_HOUR_CLS_CODE"] == "1"


def test_prepare_nxt_asking_price_subscription_message_matches_official_shape():
    subscription = RealtimeAPI().prepare_nxt_asking_price_subscription("005930")

    assert subscription.tr_id == "H0NXASP0"
    assert subscription.tr_type == "1"
    assert subscription.params == {"tr_key": "005930"}
    assert subscription.to_message() == {
        "header": {
            "tr_type": "1",
            "custtype": "P",
        },
        "body": {
            "input": {
                "tr_id": "H0NXASP0",
                "tr_key": "005930",
            }
        },
    }
    assert "ASKP1" in subscription.columns
    assert "KMID_PRC" in subscription.columns


def test_prepare_nxt_trade_subscription_uses_trade_tr_id():
    subscription = RealtimeAPI().prepare_nxt_trade_subscription("005930", subscribe=False)

    assert subscription.tr_id == "H0NXCNT0"
    assert subscription.tr_type == "0"
    assert subscription.params == {"tr_key": "005930"}
    assert "STCK_PRPR" in subscription.columns


def test_prepare_nxt_market_status_subscription_uses_market_status_tr_id():
    subscription = RealtimeAPI().prepare_nxt_market_status_subscription("005930")

    assert subscription.tr_id == "H0NXMKO0"
    assert subscription.params == {"tr_key": "005930"}
    assert "MKOP_CLS_CODE" in subscription.columns
