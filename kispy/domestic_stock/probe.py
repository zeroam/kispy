"""No-trade helpers for KRX/NXT feasibility probes."""

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .quote import PreparedDomesticQuoteRequest, QuoteAPI
from .realtime import PreparedWebSocketSubscription, RealtimeAPI

JsonDict = dict[str, Any]

SENSITIVE_KEYS = {"appkey", "appsecret", "authorization", "approval_key", "personalseckey"}


class NoTradeJsonlLogger:
    """Append prepared REST/WS probe surfaces without placing orders."""

    def __init__(
        self,
        log_path: str | Path,
        clock: Callable[[], datetime] | None = None,
    ):
        self.log_path = Path(log_path)
        self._clock = clock or (lambda: datetime.now(UTC))

    def log_quote_request(
        self,
        label: str,
        request: PreparedDomesticQuoteRequest,
        window: str,
    ) -> JsonDict:
        event = {
            "observed_at": self._observed_at(),
            "kind": "rest_request",
            "label": label,
            "window": window,
            "request": {
                "method": request.method,
                "path": request.path,
                "tr_id": request.tr_id,
                "tr_cont": request.tr_cont,
                "params": dict(request.params),
            },
        }
        self._append(event)
        return event

    def log_websocket_subscription(
        self,
        label: str,
        subscription: PreparedWebSocketSubscription,
        window: str,
        extra_headers: dict[str, str] | None = None,
    ) -> JsonDict:
        message = subscription.to_message(extra_headers=_redact_mapping(extra_headers or {}))
        event = {
            "observed_at": self._observed_at(),
            "kind": "websocket_subscription",
            "label": label,
            "window": window,
            "message": message,
            "columns": list(subscription.columns),
        }
        self._append(event)
        return event

    def _observed_at(self) -> str:
        observed_at = self._clock()
        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(tzinfo=UTC)
        return observed_at.isoformat()

    def _append(self, event: JsonDict) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False, sort_keys=True))
            f.write("\n")


def write_krx_nxt_no_trade_probe_plan(
    log_path: str | Path,
    quote_api: QuoteAPI,
    realtime_api: RealtimeAPI,
    stock_code: str,
    market_code: str = "0000",
    clock: Callable[[], datetime] | None = None,
) -> list[JsonDict]:
    logger = NoTradeJsonlLogger(log_path, clock=clock)
    return [
        logger.log_websocket_subscription(
            "nxt_asking_price",
            realtime_api.prepare_nxt_asking_price_subscription(stock_code),
            window="08:00-08:50",
        ),
        logger.log_websocket_subscription(
            "nxt_trade",
            realtime_api.prepare_nxt_trade_subscription(stock_code),
            window="08:00-08:50",
        ),
        logger.log_websocket_subscription(
            "nxt_market_status",
            realtime_api.prepare_nxt_market_status_subscription(stock_code),
            window="08:00-08:50",
        ),
        logger.log_quote_request(
            "krx_overtime_asking_price",
            quote_api.prepare_overtime_asking_price(stock_code),
            window="08:30-08:40",
        ),
        logger.log_quote_request(
            "krx_time_overtime_conclusion",
            quote_api.prepare_time_overtime_conclusion(stock_code),
            window="08:30-08:40",
        ),
        logger.log_quote_request(
            "krx_after_hour_balance",
            quote_api.prepare_after_hour_balance(market_code=market_code),
            window="08:30-08:40",
        ),
    ]


def _redact_mapping(mapping: dict[str, str]) -> dict[str, str]:
    return {key: "***" if key.lower() in SENSITIVE_KEYS else value for key, value in mapping.items()}
