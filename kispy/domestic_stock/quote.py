"""[국내주식] 기본시세
- 기본적인 시세 정보 조회 (현재가, 호가, 체결, 일별 시세 등)
"""

import requests

from kispy.auth import AuthAPI
from kispy.constants import REAL_URL, VIRTUAL_URL
from kispy.responses import BaseResponse


class QuoteAPI:
    def __init__(self, auth: AuthAPI):
        self._url = REAL_URL if auth.is_real else VIRTUAL_URL
        self._auth = auth

    def _request(self, method: str, url: str, **kwargs) -> BaseResponse:
        resp = requests.request(method, url, **kwargs)
        custom_resp = BaseResponse(status_code=resp.status_code, json=resp.json())
        custom_resp.raise_for_status()
        return custom_resp

    def get_price(self, stock_code: str) -> int:
        """
        주식 현재가 시세 API입니다. 실시간 시세를 원하신다면 웹소켓 API를 활용하세요.

        Args:
            stock_code (str): 종목코드

        Returns:
            int: 주식 현재가
        """
        path = "uapi/domestic-stock/v1/quotations/inquire-price"
        url = f"{self._url}/{path}"

        tr_id = "FHKST01010100"
        headers = self._auth.get_header()
        headers["tr_id"] = tr_id
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": stock_code,
        }

        resp = self._request(method="get", url=url, headers=headers, params=params)
        return int(resp.json["output"]["stck_prpr"])
