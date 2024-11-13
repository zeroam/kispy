from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from kispy.constants import ExchangeCode


@dataclass
class Symbol:
    symbol: str
    exchange_code: ExchangeCode
    realtime_symbol: str


@dataclass
class OHLCV:
    date: datetime
    open: str
    high: str
    low: str
    close: str
    volume: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
