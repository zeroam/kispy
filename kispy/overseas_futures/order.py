"""[해외선물옵션] 주문/계좌."""

from dataclasses import dataclass

from kispy.base import BaseAPI
from kispy.constants import OrderSide
from kispy.exceptions import KispyException


@dataclass(frozen=True)
class PreparedOverseasFuturesOrder:
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
    def prepare_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        price: float | str | None = None,
        price_type: str = "1",
        condition: str = "6",
    ) -> PreparedOverseasFuturesOrder:
        """해외선물옵션 주문[v1_해외선물-001]."""
        return PreparedOverseasFuturesOrder(
            method="post",
            path="uapi/overseas-futureoption/v1/trading/order",
            tr_id="OTFM3001U",
            body={
                "CANO": self._auth.cano,
                "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
                "OVRS_FUTR_FX_PDNO": symbol,
                "SLL_BUY_DVSN_CD": _get_side_code(side),
                "FM_LQD_USTL_CCLD_DT": "",
                "FM_LQD_USTL_CCNO": "",
                "PRIC_DVSN_CD": price_type,
                "FM_LIMIT_ORD_PRIC": "" if price is None else str(price),
                "FM_STOP_ORD_PRIC": "",
                "FM_ORD_QTY": str(quantity),
                "FM_LQD_LMT_ORD_PRIC": "",
                "FM_LQD_STOP_ORD_PRIC": "",
                "CCLD_CNDT_CD": condition,
                "CPLX_ORD_DVSN_CD": "0",
                "ECIS_RSVN_ORD_YN": "N",
                "FM_HDGE_ORD_SCRN_YN": "N",
            },
        )

    def create(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        price: float | str | None = None,
        price_type: str = "1",
        condition: str = "6",
    ) -> dict:
        order = self.prepare_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            price_type=price_type,
            condition=condition,
        )
        return self._send_prepared_order(order)

    def prepare_cancel_order(
        self,
        order_number: str,
        order_date: str,
        market_price_conversion: str = "N",
    ) -> PreparedOverseasFuturesOrder:
        """해외선물옵션 주문 취소[v1_해외선물-003]."""
        return PreparedOverseasFuturesOrder(
            method="post",
            path="uapi/overseas-futureoption/v1/trading/order-rvsecncl",
            tr_id="OTFM3003U",
            body={
                "CANO": self._auth.cano,
                "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
                "ORGN_ORD_DT": order_date,
                "ORGN_ODNO": order_number,
                "FM_LIMIT_ORD_PRIC": "",
                "FM_STOP_ORD_PRIC": "",
                "FM_LQD_LMT_ORD_PRIC": "",
                "FM_LQD_STOP_ORD_PRIC": "",
                "FM_HDGE_ORD_SCRN_YN": "N",
                "FM_MKPR_CVSN_YN": market_price_conversion,
            },
        )

    def cancel(self, order_number: str, order_date: str, market_price_conversion: str = "N") -> dict:
        order = self.prepare_cancel_order(
            order_number=order_number,
            order_date=order_date,
            market_price_conversion=market_price_conversion,
        )
        return self._send_prepared_order(order)

    def _send_prepared_order(self, order: PreparedOverseasFuturesOrder) -> dict:
        url = f"{self._url}/{order.path}"
        headers = self._auth.get_header()
        headers["tr_id"] = order.tr_id
        resp = self._request(method=order.method, url=url, headers=headers, json=order.body)
        return resp.json["output"]  # type: ignore[no-any-return]


def _get_side_code(side: OrderSide) -> str:
    if side == "sell":
        return "01"
    if side == "buy":
        return "02"
    raise KispyException(f"Invalid side: {side}")
