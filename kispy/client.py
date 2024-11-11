import logging
from datetime import datetime
from decimal import Decimal
from typing import Literal

from kispy.auth import KisAuth
from kispy.constants import (
    OHLCV,
    PERIOD_TO_MINUTES,
    REAL_URL,
    VIRTUAL_URL,
    AccountSummary,
    Balance,
    ExchangeLongCodeMap,
    Nation,
    PendingOrder,
    Period,
    Position,
    Symbol,
)
from kispy.domestic_stock import DomesticStock
from kispy.overseas_stock import OverseasStock
from kispy.utils import get_symbol_map

logger = logging.getLogger(__name__)


class KisClient:
    def __init__(
        self,
        auth: KisAuth,
    ) -> None:
        """KIS API 클라이언트를 초기화합니다.

        Args:
            app_key (str): 한국투자증권에서 발급받은 앱키
            app_secret (str): 한국투자증권에서 발급받은 앱시크릿
            account_no (str): 사용할 계좌번호 (예: "5000000000-01")
            is_real (bool, optional): 실전투자 여부. 기본값은 False (모의투자).

        Note:
            account_no는 "계좌번호-상품코드" 형식으로 입력해야 합니다.

        Raises:
            ValueError: account_no가 올바른 형식이 아닐 경우 발생

        Example:
            >>> client = KISClient("your_app_key", "your_app_secret", "5000000000-01")
        """
        self._url = REAL_URL if auth.is_real else VIRTUAL_URL
        self._auth = auth
        self.domestic_stock = DomesticStock(auth=self._auth)
        self.overseas_stock = OverseasStock(auth=self._auth)


class KisClientV2:
    def __init__(self, auth: KisAuth, nation: Nation):
        self.client = KisClient(auth)
        self.nation = nation
        self._market: dict[str, Symbol] = {}

    def load_market_data(self, reload: bool = False) -> None:
        if not self._market or reload:
            self._market = get_symbol_map(self.nation)

    def get_price(self, symbol: str) -> str:
        if self.nation == "KR":
            # TODO: 국내주식 현재가 조회
            raise NotImplementedError("국내주식 현재가 조회는 아직 구현되지 않았습니다.")

        self.load_market_data()
        market_symbol = self._market[symbol]
        return self.client.overseas_stock.quote.get_price(market_symbol.symbol, market_symbol.exchange_code)

    def fetch_balance(self) -> Balance:
        """잔고 조회

        Returns:
            Balance: 외화 잔고
        """
        if self.nation == "KR":
            # TODO: 국내주식 잔고 조회
            raise NotImplementedError("국내주식 잔고 조회는 아직 구현되지 않았습니다.")

        # TODO: 다른 국가 지원
        response = self.client.overseas_stock.account.inquire_psamount("AAPL", "NASD")
        return Balance(
            available_balance=response["ord_psbl_frcr_amt"],
            buyable_balance=response["ovrs_ord_psbl_amt"],
            exchange_rate=response["exrt"],
            currency=response["tr_crcy_cd"],
        )

    def fetch_positions(self) -> list[Position]:
        """보유종목 조회

        Returns:
            list[Position]: 외화 보유종목
        """
        if self.nation == "KR":
            # TODO: 국내주식 보유종목 조회
            raise NotImplementedError("국내주식 보유종목 조회는 아직 구현되지 않았습니다.")

        # TODO: 다른 국가 지원
        response = self.client.overseas_stock.account.inquire_balance(exchange_code="NASD", currency="USD")
        # TODO: 대출유형 추가 필요
        return [
            Position(
                symbol=position["ovrs_pdno"],
                item_name=position["ovrs_item_name"],
                quantity=position["ord_psbl_qty"],
                average_price=position["pchs_avg_pric"],
                unrealized_pnl=position["frcr_evlu_pfls_amt"],
                pnl_percentage=position["evlu_pfls_rt"],
                current_price=position["now_pric2"],
                market_value=position["ovrs_stck_evlu_amt"],
            )
            for position in response["output1"]
        ]

    def fetch_pending_orders(self) -> list[PendingOrder]:
        if self.nation == "KR":
            # TODO: 국내주식 예약주문 조회
            raise NotImplementedError("국내주식 예약주문 조회는 아직 구현되지 않았습니다.")

        # TODO: 다른 국가 지원
        orders = self.client.overseas_stock.account.inquire_nccs("NASD")
        result: list[PendingOrder] = []
        for order in orders:
            requested_price = order["ft_ord_unpr3"]
            remaining_quantity = order["nccs_qty"]
            locked_amount = Decimal(requested_price) * Decimal(remaining_quantity)
            result.append(
                PendingOrder(
                    order_id=order["odno"],
                    symbol=order["pdno"],
                    side="buy" if order["sll_buy_dvsn_cd_name"] == "02" else "sell",
                    requested_price=requested_price,
                    requested_quantity=order["ft_ord_qty"],
                    filled_amount=order["ft_ccld_qty"],
                    average_price=order["ft_ccld_unpr3"],
                    remaining_quantity=remaining_quantity,
                    order_amount=order["ft_ccld_amt3"],
                    locked_amount=str(locked_amount),
                )
            )
        return result

    def fetch_account_summary(self) -> AccountSummary:
        """총 자산 정보를 조회"""
        balance = self.fetch_balance()
        positions = self.fetch_positions()
        pending_orders = self.fetch_pending_orders()
        return AccountSummary.create(balance, positions, pending_orders)

    def fetch_ohlcv(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
        period: Period = "d",
        is_adjust: bool = True,
        desc: bool = False,
        limit: int | None = None,
    ) -> list[OHLCV]:
        """
        주식 기간별 시세 조회

        Args:
            symbol (str): 종목코드
            start_date (str): 조회시작일자 ("YYYY-MM-DD" 형식)
            end_date (str): 조회종료일자 ("YYYY-MM-DD" 형식)
            period (Period): 조회기간, 기본값은 "1d"
            is_adjust (bool): 수정주가 여부, 기본값은 True
            desc (bool): 시간 역순 정렬 여부, 기본값은 False

        Returns:
            list[dict]: 주식 기간별 시세
        """
        if self.nation == "KR":
            # TODO: 국내주식 시세 조회
            return []

        self.load_market_data()
        market_symbol = self._market[symbol]

        exchange_code = market_symbol.exchange_code
        if period in ["d", "w", "M"]:
            histories = self.client.overseas_stock.quote.get_stock_price_history(
                symbol=market_symbol.symbol,
                exchange_code=exchange_code,
                start_date=start_date,
                end_date=end_date,
                period=period,
                is_adjust=is_adjust,
                desc=desc,
                limit=limit,
            )
            result = [
                OHLCV(
                    date=datetime.strptime(history["xymd"], "%Y%m%d"),
                    open=history["open"],
                    high=history["high"],
                    low=history["low"],
                    close=history["clos"],
                    volume=history["tvol"],
                )
                for history in histories
            ]
        else:
            minutes = PERIOD_TO_MINUTES[period]
            histories = self.client.overseas_stock.quote.get_stock_price_history_by_minute(
                symbol=market_symbol.symbol,
                exchange_code=exchange_code,
                period=minutes,
                start_date=start_date,
                end_date=end_date,
                desc=desc,
                limit=limit,
            )
            result = [
                OHLCV(
                    date=datetime.strptime(history["xymd"] + history["xhms"], "%Y%m%d%H%M%S"),
                    open=history["open"],
                    high=history["high"],
                    low=history["low"],
                    close=history["last"],
                    volume=history["evol"],
                )
                for history in histories
            ]

        return result

    def create_order(
        self,
        symbol: str,
        side: Literal["buy", "sell"],
        price: float,
        quantity: int,
    ) -> str:
        """주문 생성

        Args:
            symbol (str): 종목코드
            side (Literal["buy", "sell"]): 주문 방향
            price (float): 주문 가격
            quantity (int): 주문 수량

        Returns:
            str: 주문 ID
        """
        if self.nation == "KR":
            # TODO: 국내주식 주문
            raise NotImplementedError("국내주식 주문은 아직 구현되지 않았습니다.")

        self.load_market_data()
        market_symbol = self._market[symbol]
        exchange_code = ExchangeLongCodeMap[market_symbol.exchange_code]

        if side == "buy":
            order = self.client.overseas_stock.order.buy(
                symbol=market_symbol.symbol,
                exchange_code=exchange_code,
                quantity=quantity,
                price=price,
            )
        elif side == "sell":
            order = self.client.overseas_stock.order.sell(
                symbol=market_symbol.symbol,
                exchange_code=exchange_code,
                quantity=quantity,
                price=price,
            )

        return order["ODNO"]  # type: ignore[no-any-return]

    def cancel_order(self, symbol: str, order_id: str) -> str:
        """주문취소

        Args:
            symbol (str): 종목코드
            order_id (str): 주문번호

        Returns:
            str: 주문번호
        """
        self.load_market_data()
        market_symbol = self._market[symbol]
        exchange_code = ExchangeLongCodeMap[market_symbol.exchange_code]
        resp = self.client.overseas_stock.order.cancel(
            symbol=market_symbol.symbol,
            exchange_code=exchange_code,
            order_number=order_id,
        )

        return resp["ODNO"]  # type: ignore[no-any-return]
