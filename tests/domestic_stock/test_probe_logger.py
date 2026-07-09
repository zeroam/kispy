import json
from datetime import UTC, datetime
from types import SimpleNamespace

from kispy.domestic_stock.probe import NoTradeJsonlLogger, write_krx_nxt_no_trade_probe_plan
from kispy.domestic_stock.quote import QuoteAPI
from kispy.domestic_stock.realtime import RealtimeAPI


def make_quote_api() -> QuoteAPI:
    auth = SimpleNamespace(
        is_real=True,
        get_header=lambda: {"authorization": "Bearer token", "appkey": "key", "appsecret": "secret"},
    )
    return QuoteAPI(auth)


def fixed_clock() -> datetime:
    return datetime(2026, 7, 9, 8, 30, tzinfo=UTC)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_no_trade_logger_writes_prepared_quote_request_without_sending(tmp_path):
    log_path = tmp_path / "probe.jsonl"
    logger = NoTradeJsonlLogger(log_path, clock=fixed_clock)

    event = logger.log_quote_request(
        "krx_time_overtime_conclusion",
        make_quote_api().prepare_time_overtime_conclusion("005930"),
        window="08:30-08:40",
    )

    rows = read_jsonl(log_path)
    assert rows == [event]
    assert event == {
        "observed_at": "2026-07-09T08:30:00+00:00",
        "kind": "rest_request",
        "label": "krx_time_overtime_conclusion",
        "window": "08:30-08:40",
        "request": {
            "method": "get",
            "path": "uapi/domestic-stock/v1/quotations/inquire-time-overtimeconclusion",
            "tr_id": "FHPST02310000",
            "tr_cont": "",
            "params": {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": "005930",
                "FID_HOUR_CLS_CODE": "1",
            },
        },
    }


def test_no_trade_logger_writes_redacted_websocket_subscription(tmp_path):
    log_path = tmp_path / "probe.jsonl"
    logger = NoTradeJsonlLogger(log_path, clock=fixed_clock)

    event = logger.log_websocket_subscription(
        "nxt_trade",
        RealtimeAPI().prepare_nxt_trade_subscription("005930"),
        window="08:00-08:50",
        extra_headers={"approval_key": "secret-approval"},
    )

    rows = read_jsonl(log_path)
    assert rows == [event]
    assert event["kind"] == "websocket_subscription"
    assert event["message"]["header"]["approval_key"] == "***"
    assert event["message"]["body"]["input"] == {
        "tr_id": "H0NXCNT0",
        "tr_key": "005930",
    }
    assert "STCK_PRPR" in event["columns"]
    assert "secret-approval" not in log_path.read_text()


def test_write_krx_nxt_no_trade_probe_plan_logs_expected_read_surfaces(tmp_path):
    log_path = tmp_path / "probe.jsonl"

    events = write_krx_nxt_no_trade_probe_plan(
        log_path=log_path,
        quote_api=make_quote_api(),
        realtime_api=RealtimeAPI(),
        stock_code="005930",
        clock=fixed_clock,
    )

    labels = [event["label"] for event in events]
    assert labels == [
        "nxt_asking_price",
        "nxt_trade",
        "nxt_market_status",
        "krx_overtime_asking_price",
        "krx_time_overtime_conclusion",
        "krx_after_hour_balance",
    ]
    rows = read_jsonl(log_path)
    assert rows == events
    assert rows[0]["window"] == "08:00-08:50"
    assert rows[3]["window"] == "08:30-08:40"
    assert rows[4]["request"]["tr_id"] == "FHPST02310000"
