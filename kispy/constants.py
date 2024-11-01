from dataclasses import dataclass
from datetime import datetime
from typing import Literal

REAL_URL = "https://openapi.koreainvestment.com:9443"  # 실전투자 API
VIRTUAL_URL = "https://openapivts.koreainvestment.com:29443"  # 모의투자 API

# Rate Limits (calls per second)
RATE_LIMIT_PER_SECOND = 19  # Maximum 19 calls per second
RATE_LIMIT_WINDOW = 1.0  # Window size in seconds

Nation = Literal["KR", "US", "JP", "CN", "HK", "VN"]
ExchangeCode = Literal["NAS", "NYS", "AMS", "HKS", "HNX", "HSX", "SHI", "SHS", "SZI", "SZS", "TSE"]
LongExchangeCode = Literal["NASD", "NYSE", "AMEX", "SEHK", "SHAA", "SZAA", "TKSE", "HASE", "VNSE"]

NationExchangeCodeMap: dict[Nation, list[ExchangeCode]] = {
    "US": ["NAS", "NYS", "AMS"],
    "HK": ["HKS"],
    "JP": ["TSE"],
    "CN": ["SHS"],
    "VN": ["HSX", "HNX"],
}

ExchangeLongCodeMap: dict[ExchangeCode, LongExchangeCode] = {
    "NAS": "NASD",  # 나스닥
    "NYS": "NYSE",  # 뉴욕
    "AMS": "AMEX",  # 아멕스
    "HKS": "SEHK",  # 홍콩
    "SHS": "SHAA",  # 중국상해
    "SHI": "SHAA",  # 중국상해지수
    "SZS": "SZAA",  # 중국심천
    "SZI": "SZAA",  # 중국심천지수
    "HSX": "HASE",  # 베트남 하노이
    "HNX": "VNSE",  # 베트남 호치민
}

Period = Literal[
    "1m",
    "3m",
    "5m",
    "10m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "d",
    "w",
    "M",
]


@dataclass
class Symbol:
    symbol: str
    exchange_code: ExchangeCode
    realtime_symbol: str


@dataclass
class OHLCV:
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
