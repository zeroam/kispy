from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal, Self

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


@dataclass
class Balance:
    available_balance: str  # 주문가능외화금액
    buyable_balance: str  # 수수료까지 고려한 매수가능외화금액 (거래수수료 0.25% 포함)
    exchange_rate: str  # 환율
    currency: Currency  # 통화


@dataclass
class Position:
    symbol: str  # 종목코드
    item_name: str  # 종목명
    quantity: str  # 보유수량
    average_price: str  # 평균단가
    unrealized_pnl: str  # 외화평가손익금액
    pnl_percentage: str  # 평가손익율(%)
    current_price: str  # 현재가격
    market_value: str  # 평가금액


@dataclass
class PendingOrder:
    order_id: str  # 주문번호
    symbol: str  # 종목코드
    side: OrderSide  # 주문유형
    requested_price: str  # 주문가격
    requested_quantity: str  # 주문수량
    filled_amount: str  # 체결수량
    remaining_quantity: str  # 미체결수량
    average_price: str  # 체결가격
    order_amount: str  # 체결금액
    locked_amount: str  # 주문중금액


@dataclass
class AccountSummary:
    total_balance: str  # 총 자산
    locked_balance: str  # 주문중금액
    available_balance: str  # 주문가능외화금액
    buyable_balance: str  # 수수료까지 고려한 매수가능외화금액 (거래수수료 0.25% 포함)
    exchange_rate: str  # 환율
    currency: Currency  # 통화
    total_unrealized_pnl: str  # 총 외화평가손익금액
    total_pnl_percentage: str  # 총 평가손익율(%)
    positions: list[Position]
    pending_orders: list[PendingOrder]

    @classmethod
    def create(cls, balance: Balance, positions: list[Position], pending_orders: list[PendingOrder]) -> Self:
        # TODO: 원화 예수금 조회
        available_balance = Decimal(balance.available_balance)
        total_position_market_value = sum(Decimal(position.market_value) for position in positions)
        total_position_price = sum(Decimal(position.average_price) * Decimal(position.quantity) for position in positions)
        total_locked_balance = sum(Decimal(order.locked_amount) for order in pending_orders)
        total_balance = available_balance + total_position_market_value + total_locked_balance
        total_unrealized_pnl = sum(Decimal(position.unrealized_pnl) for position in positions)
        total_pnl_percentage = (total_position_market_value - total_position_price) / total_position_price * 100
        return cls(
            total_balance=str(total_balance),
            locked_balance=str(total_locked_balance),
            available_balance=str(available_balance),
            buyable_balance=str(balance.buyable_balance),
            exchange_rate=balance.exchange_rate,
            currency=balance.currency,
            total_unrealized_pnl=str(total_unrealized_pnl),
            total_pnl_percentage=f"{total_pnl_percentage:.2f}",
            positions=positions,
            pending_orders=pending_orders,
        )
