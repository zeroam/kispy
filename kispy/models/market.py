from dataclasses import dataclass
from datetime import datetime
from typing import Any, Self

from kispy.constants import ExchangeCode
from kispy.models.base import CustomBaseModel


@dataclass
class Symbol:
    symbol: str
    exchange_code: ExchangeCode
    realtime_symbol: str


class OHLCV(CustomBaseModel):
    date: datetime
    open: str
    high: str
    low: str
    close: str
    volume: str

    @classmethod
    def from_response(cls, response: dict[str, Any]) -> Self:
        if "xhms" in response:
            date = datetime.strptime(response["xymd"] + response["xhms"], "%Y%m%d%H%M%S")
            volume = response["evol"]
            close = response["last"]
        else:
            date = datetime.strptime(response["xymd"], "%Y%m%d")
            volume = response["tvol"]
            close = response["clos"]

        return cls(
            date=date,
            open=response["open"],
            high=response["high"],
            low=response["low"],
            close=close,
            volume=volume,
        )
