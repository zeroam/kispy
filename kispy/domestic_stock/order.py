"""[국내주식] 주문/계좌
- 주문 관련 기능 (매수, 매도, 정정, 취소 등)
"""

import requests

from kispy.auth import AuthAPI
from kispy.constants import REAL_URL, VIRTUAL_URL
from kispy.responses import BaseResponse


class OrderAPI:
    def __init__(self, auth: AuthAPI):
        self._url = REAL_URL if auth.is_real else VIRTUAL_URL
        self._auth = auth

    def _request(self, method: str, url: str, **kwargs) -> BaseResponse:
        resp = requests.request(method, url, **kwargs)
        custom_resp = BaseResponse(status_code=resp.status_code, json=resp.json())
        custom_resp.raise_for_status()
        return custom_resp

    def buy(self, stock_code: str, quantity: int, price: float) -> dict:
        """
        주식주문(현금)[v1_국내주식-001] - 매수
        """
        path = "uapi/domestic-stock/v1/trading/order-cash"
        url = f"{self._url}/{path}"

        if self._auth.is_real:
            tr_id = "TTTC0802U"  # 실전투자
        else:
            tr_id = "VTTC0802U"  # 모의투자

        headers = self._auth.get_header()
        headers["tr_id"] = tr_id
        params = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "PDNO": stock_code,
            "ORD_DVSN": "00",  # 주문구분: 00-지정가, 01-시장가
            "ORD_QTY": str(quantity),  # 주문수량
            "ORD_UNPR": str(price),
        }

        resp = self._request(method="post", url=url, headers=headers, json=params)
        return resp.json

    def sell(self) -> dict:
        """
        주식주문(현금)[v1_국내주식-001] - 매도
        """
        return {}
