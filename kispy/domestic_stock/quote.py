"""[국내주식] 기본시세
- 기본적인 시세 정보 조회 (현재가, 호가, 체결, 일별 시세 등)
"""

from datetime import datetime, timedelta

import requests

from kispy.auth import KisAuth
from kispy.constants import REAL_URL, VIRTUAL_URL
from kispy.responses import BaseResponse


class QuoteAPI:
    def __init__(self, auth: KisAuth):
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

    def get_stock_price_history(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        period: str = "D",
        is_adjust: bool = True,
    ) -> list[dict]:
        """
        국내주식기간별시세(일/주/월/년) API입니다.

        Args:
            stock_code (str): 종목코드
            start_date (str): 조회시작일자 ("YYYY-MM-DD" 형식)
            end_date (str | None): 조회종료일자 ("YYYY-MM-DD" 형식), 기본값은 오늘
            period (str): 조회기간, 기본값은 "D" (일) (옵션: "D" (일), "W" (주), "M" (월), "Y" (년))
            is_adjust (bool): 수정주가 여부, 기본값은 True

        Returns:
            list[dict]: 주식 기간별 시세 (시간 역순 정렬)
        """
        parsed_start_date = self._parse_date(start_date)
        parsed_end_date = min(
            self._parse_date(end_date or datetime.now().strftime("%Y-%m-%d")),
            datetime.now(),
        )

        result = []
        cur_end_date = parsed_end_date
        while cur_end_date >= parsed_start_date:
            cur_start_date = min(cur_end_date - timedelta(days=99), parsed_start_date)
            resp = self._request(
                "GET",
                f"{self._url}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
                headers={**self._auth.get_header(), "tr_id": "FHKST03010100"},
                params={
                    "FID_COND_MRKT_DIV_CODE": "J",
                    "FID_INPUT_ISCD": stock_code,
                    "FID_INPUT_DATE_1": cur_start_date.strftime("%Y%m%d"),
                    "FID_INPUT_DATE_2": cur_end_date.strftime("%Y%m%d"),
                    "FID_PERIOD_DIV_CODE": period,
                    "FID_ORG_ADJ_PRC": "0" if is_adjust else "1",
                },
            )
            items = [
                data
                for data in resp.json["output2"]
                if data and datetime.strptime(data["stck_bsop_date"], "%Y%m%d") >= parsed_start_date
            ]
            if not items:
                break

            result.extend(items)
            cur_end_date = datetime.strptime(items[-1]["stck_bsop_date"], "%Y%m%d") - timedelta(days=1)

        return result

    def _parse_date(self, date_str: str) -> datetime:
        return datetime.strptime(date_str, "%Y-%m-%d")
