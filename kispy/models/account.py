from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Self

from kispy.constants import Currency, OrderSide, OrderStatus
from kispy.models.base import CustomBaseModel


class Balance(CustomBaseModel):
    available_balance: str  # 주문가능외화금액
    buyable_balance: str  # 수수료까지 고려한 매수가능외화금액 (거래수수료 0.25% 포함)
    integrated_balance: str  # 한국투자 앱 해외주식 주문화면내 "통합"인경우 주문가능 금액
    exchange_rate: str  # 환율
    currency: Currency  # 통화

    @classmethod
    def from_response(cls, response: dict[str, Any]) -> Self:
        return cls(
            available_balance=response["ord_psbl_frcr_amt"],
            buyable_balance=response["ovrs_ord_psbl_amt"],
            integrated_balance=response["frcr_ord_psbl_amt1"],
            exchange_rate=response["exrt"],
            currency=response["tr_crcy_cd"],
        )


class Position(CustomBaseModel):
    symbol: str  # 종목코드
    item_name: str  # 종목명
    quantity: str  # 보유수량
    average_price: str  # 평균단가
    unrealized_pnl: str  # 외화평가손익금액
    pnl_percentage: str  # 평가손익율(%)
    current_price: str  # 현재가격
    market_value: str  # 평가금액

    @classmethod
    def from_response(cls, response: dict[str, Any]) -> Self:
        # TODO: 대출유형 추가 필요
        return cls(
            symbol=response["ovrs_pdno"],
            item_name=response["ovrs_item_name"],
            quantity=response["ord_psbl_qty"],
            average_price=response["pchs_avg_pric"],
            unrealized_pnl=response["frcr_evlu_pfls_amt"],
            pnl_percentage=response["evlu_pfls_rt"],
            current_price=response["now_pric2"],
            market_value=response["ovrs_stck_evlu_amt"],
        )


class PendingOrder(CustomBaseModel):
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

    @classmethod
    def from_response(cls, response: dict[str, Any]) -> Self:
        requested_price = response["ft_ord_unpr3"]
        remaining_quantity = response["nccs_qty"]
        locked_amount = Decimal(requested_price) * Decimal(remaining_quantity)
        return cls(
            order_id=response["odno"],
            symbol=response["pdno"],
            side="buy" if response["sll_buy_dvsn_cd_name"] == "02" else "sell",
            requested_price=requested_price,
            requested_quantity=response["ft_ord_qty"],
            filled_amount=response["ft_ccld_qty"],
            average_price=response["ft_ccld_unpr3"],
            remaining_quantity=remaining_quantity,
            order_amount=response["ft_ccld_amt3"],
            locked_amount=str(locked_amount),
        )


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


class Order(CustomBaseModel):
    order_id: str
    symbol: str
    side: OrderSide
    status: OrderStatus
    requested_price: str  # 주문가격
    requested_quantity: str  # 주문수량
    filled_quantity: str  # 체결수량
    average_price: str  # 체결가격
    filled_amount: str  # 체결금액
    reject_reason: str  # 거부사유
    order_date: datetime  # 주문일시

    @classmethod
    def from_response(cls, response: dict[str, Any]) -> Self:
        order_date = datetime.strptime(response["ord_dt"] + response["ord_tmd"], "%Y%m%d%H%M%S")
        process_status = response["prcs_stat_name"]
        reject_reason = response["rjct_rson_name"]
        revise_cancel_status = response["rvse_cncl_dvsn_name"]
        status: OrderStatus = "open"
        if process_status == "완료":
            if reject_reason == "DFD 장종료로 취소":
                status = "expired"
            elif reject_reason:  # NOTE: 해당 케이스 검증 필요
                status = "rejected"
            elif revise_cancel_status == "취소":  # NOTE: 실제로 취소 검증 필요
                status = "canceled"
            else:
                status = "closed"
        elif process_status == "거부":
            status = "rejected"

        return cls(
            order_id=response["odno"],
            symbol=response["pdno"],
            side="buy" if response["sll_buy_dvsn_cd_name"] == "매수" else "sell",
            status=status,
            requested_price=response["ft_ord_unpr3"],
            requested_quantity=response["ft_ord_qty"],
            filled_quantity=response["ft_ccld_qty"],
            average_price=response["ft_ccld_unpr3"],
            filled_amount=response["ft_ccld_amt3"],
            reject_reason=reject_reason,
            order_date=order_date,
        )
