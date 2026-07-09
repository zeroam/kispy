"""[국내주식] 주문/계좌
- 주문 관련 기능 (매수, 매도, 정정, 취소 등)
"""

from dataclasses import dataclass
from typing import Literal

from kispy.base import BaseAPI

DomesticExchange = Literal["KRX", "NXT", "SOR"]
DomesticOrderSide = Literal["buy", "sell"]


@dataclass(frozen=True)
class PreparedDomesticOrder:
    method: str
    path: str
    tr_id: str
    body: dict[str, str]

    def redacted_body(self) -> dict[str, str]:
        return {
            **self.body,
            "CANO": "***",
            "ACNT_PRDT_CD": "***",
        }


class OrderAPI(BaseAPI):
    def prepare_cash_order(
        self,
        stock_code: str,
        side: DomesticOrderSide,
        quantity: int,
        price: int | str,
        exchange: DomesticExchange = "KRX",
        order_type: str = "00",
        sell_type: str = "01",
        condition_price: str = "",
    ) -> PreparedDomesticOrder:
        path = "uapi/domestic-stock/v1/trading/order-cash"
        tr_id = _get_cash_order_tr_id(side, self._auth.is_real)
        body = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "PDNO": stock_code,
            "ORD_DVSN": order_type,
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price),
            "EXCG_ID_DVSN_CD": exchange,
            "SLL_TYPE": sell_type if side == "sell" else "",
            "CNDT_PRIC": condition_price,
        }
        return PreparedDomesticOrder(method="post", path=path, tr_id=tr_id, body=body)

    def prepare_reservation_order(
        self,
        stock_code: str,
        side: DomesticOrderSide,
        quantity: int,
        price: int | str,
        order_type: str = "00",
        balance_type: str = "10",
        loan_date: str = "",
        reservation_end_date: str = "",
        lending_date: str = "",
    ) -> PreparedDomesticOrder:
        path = "uapi/domestic-stock/v1/trading/order-resv"
        body = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "PDNO": stock_code,
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price),
            "SLL_BUY_DVSN_CD": _get_reservation_side_code(side),
            "ORD_DVSN_CD": order_type,
            "ORD_OBJT_CBLC_DVSN_CD": balance_type,
        }
        if loan_date:
            body["LOAN_DT"] = loan_date
        if reservation_end_date:
            body["RSVN_ORD_END_DT"] = reservation_end_date
        if lending_date:
            body["LDNG_DT"] = lending_date

        return PreparedDomesticOrder(method="post", path=path, tr_id="CTSC0008U", body=body)

    def order_cash(
        self,
        stock_code: str,
        side: DomesticOrderSide,
        quantity: int,
        price: int | str,
        exchange: DomesticExchange = "KRX",
        order_type: str = "00",
    ) -> dict:
        """주식주문(현금)[v1_국내주식-001]."""
        order = self.prepare_cash_order(
            stock_code=stock_code,
            side=side,
            quantity=quantity,
            price=price,
            exchange=exchange,
            order_type=order_type,
        )
        return self._send_prepared_order(order)

    def order_reservation(
        self,
        stock_code: str,
        side: DomesticOrderSide,
        quantity: int,
        price: int | str,
        order_type: str = "00",
    ) -> dict:
        """주식예약주문[v1_국내주식-017]."""
        order = self.prepare_reservation_order(
            stock_code=stock_code,
            side=side,
            quantity=quantity,
            price=price,
            order_type=order_type,
        )
        return self._send_prepared_order(order)

    def buy(
        self,
        stock_code: str,
        quantity: int,
        price: int | str,
        exchange: DomesticExchange = "KRX",
        order_type: str = "00",
    ) -> dict:
        """주식주문(현금)[v1_국내주식-001] - 매수."""
        return self.order_cash(
            stock_code=stock_code,
            side="buy",
            quantity=quantity,
            price=price,
            exchange=exchange,
            order_type=order_type,
        )

    def sell(
        self,
        stock_code: str,
        quantity: int,
        price: int | str,
        exchange: DomesticExchange = "KRX",
        order_type: str = "00",
    ) -> dict:
        """주식주문(현금)[v1_국내주식-001] - 매도."""
        return self.order_cash(
            stock_code=stock_code,
            side="sell",
            quantity=quantity,
            price=price,
            exchange=exchange,
            order_type=order_type,
        )

    def _send_prepared_order(self, order: PreparedDomesticOrder) -> dict:
        url = f"{self._url}/{order.path}"
        headers = self._auth.get_header()
        headers["tr_id"] = order.tr_id
        resp = self._request(method=order.method, url=url, headers=headers, json=order.body)
        return resp.json


def _get_cash_order_tr_id(side: DomesticOrderSide, is_real: bool) -> str:
    if is_real:
        return "TTTC0012U" if side == "buy" else "TTTC0011U"
    return "VTTC0012U" if side == "buy" else "VTTC0011U"


def _get_reservation_side_code(side: DomesticOrderSide) -> str:
    return "02" if side == "buy" else "01"
