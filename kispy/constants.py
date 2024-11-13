from typing import Literal

from zoneinfo import ZoneInfo

REAL_URL = "https://openapi.koreainvestment.com:9443"  # 실전투자 API
VIRTUAL_URL = "https://openapivts.koreainvestment.com:29443"  # 모의투자 API

# Rate Limits (calls per second)
RATE_LIMIT_PER_SECOND = 19  # Maximum 19 calls per second
RATE_LIMIT_WINDOW = 1.0  # Window size in seconds

Nation = Literal["KR", "US", "JP", "CN", "HK", "VN"]
ExchangeCode = Literal["NAS", "NYS", "AMS", "HKS", "HNX", "HSX", "SHI", "SHS", "SZI", "SZS", "TSE", "BAY", "BAQ", "BAA"]
LongExchangeCode = Literal["NASD", "NYSE", "AMEX", "SEHK", "SHAA", "SZAA", "TKSE", "HASE", "VNSE"]
Currency = Literal["USD", "HKD", "CNY", "JPY", "VND"]
OrderSide = Literal["buy", "sell"]
OrderStatus = Literal["open", "closed", "canceled", "rejected", "expired"]


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

TimeZoneMap: dict[ExchangeCode, ZoneInfo] = {
    "HKS": ZoneInfo("Asia/Hong_Kong"),
    "NYS": ZoneInfo("America/New_York"),
    "NAS": ZoneInfo("America/New_York"),
    "AMS": ZoneInfo("Europe/Amsterdam"),
    "TSE": ZoneInfo("Asia/Tokyo"),
    "SHS": ZoneInfo("Asia/Shanghai"),
    "SZS": ZoneInfo("Asia/Shanghai"),
    "SHI": ZoneInfo("Asia/Shanghai"),
    "SZI": ZoneInfo("Asia/Shanghai"),
    "HSX": ZoneInfo("Asia/Ho_Chi_Minh"),
    "HNX": ZoneInfo("Asia/Ho_Chi_Minh"),
    "BAY": ZoneInfo("America/New_York"),
    "BAQ": ZoneInfo("America/New_York"),
    "BAA": ZoneInfo("America/New_York"),
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

PERIOD_TO_MINUTES: dict[Period, str] = {
    "1m": "1",
    "3m": "3",
    "5m": "5",
    "10m": "10",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "2h": "120",
    "4h": "240",
}
