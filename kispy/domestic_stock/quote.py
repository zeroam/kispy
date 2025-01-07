"""[국내주식] 기본시세
- 기본적인 시세 정보 조회 (현재가, 호가, 체결, 일별 시세 등)
"""

from datetime import datetime, timedelta

from kispy.base import BaseAPI


class QuoteAPI(BaseAPI):
    def get_price(self, symbol: str) -> float:
        """주식 현재가 시세 API[v1_국내주식-008]
        입니다. 실시간 시세를 원하신다면 웹소켓 API를 활용하세요.

        Args:
            symbol (str): 종목코드

        Returns:
            float: 주식 현재가
        """
        path = "uapi/domestic-stock/v1/quotations/inquire-price"
        url = f"{self._url}/{path}"

        tr_id = "FHKST01010100"
        headers = self._auth.get_header()
        headers["tr_id"] = tr_id
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": symbol,
        }

        resp = self._request(method="get", url=url, headers=headers, params=params)
        return float(resp.json["output"]["stck_prpr"])

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
    
    def get_stock_price_history_by_minute(
        self,
        symbol: str,
        time: str | None = None,
        limit: int | None = 30,
        desc: bool = False,
    ) -> list[dict]:
        """주식당일분봉조회[v1_국내주식-022]
        당일 분봉 데이터만 제공됩니다. (전일자 분봉 미제공)

        Args:
            symbol (str): 종목코드
            time (str | None): 조회 시작시간 (HHMMSS 형식, 예: "123000"은 12시 30분부터 조회) None인 경우 현재시각부터 조회
            limit (int): 조회 건수, 기본값 30건
            desc (bool): 시간 역순 정렬 여부, 기본값은 False (False: 과거순 정렬, True: 최신순 정렬)

        Returns:
            list[dict]: 주식 분봉 시세

        Note:
            - time에 미래 시각을 입력하면 현재 시각 기준으로 조회됩니다.
            - output2의 첫번째 배열의 체결량(cntg_vol)은 첫체결이 발생되기 전까지는 이전 분봉의 체결량이 표시됩니다.
            - 한 번의 API 호출로 최대 30건의 데이터를 가져올 수 있으며, 여러 번 호출하여 더 많은 데이터를 가져올 수 있습니다.
            - 개선 가능 사항 : 
                - ETF, ETN의 분봉 데이터를 사용하여 국내 지수 분봉 데이터 추가 조회 가능
                - 섹터/업종별 지수 추가 조회 가능
        """
        path = "uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
        url = f"{self._url}/{path}"

        headers = self._auth.get_header()
        headers["tr_id"] = "FHKST03010200"

        if not time:
            time = datetime.now().replace(second=0).strftime("%H%M%S")

        result: list[dict] = []
        now = datetime.now()
        today = now.strftime("%Y%m%d")
        current_time = time if time < now.strftime("%H%M%S") else now.strftime("%H%M%S")

        while limit is None or len(result) < limit:
            params={
                "FID_COND_MRKT_DIV_CODE": "J", # 시장 분류 코드 (J : 주식)
                "FID_INPUT_ISCD": symbol, # 종목코드
                "FID_INPUT_HOUR_1": current_time, # 조회 시작 시간
                "FID_ETC_CLS_CODE": "", # 종목 분류 코드 (기본값: 빈 문자열)
                "FID_PW_DATA_INCU_YN": "N", # 데이터 포함 여부 (기본값: "N")
            }

            resp = self._request(method="get", url=url, headers=headers, params=params)

            records = list(resp.json["output2"])
            if not records:
                break

            for record in records:
                record["stck_cntg_hour"] = self._parse_date(f"{today}{record['stck_cntg_hour']}")

            if limit is not None:
                remaining = limit - len(result)
                records = records[:remaining]

            result.extend(records)

            if limit is not None and len(result) >= limit:
                break

            last_record = records[-1]
            if "stck_cntg_hour" not in last_record:
                break

            current_time = self._get_next_keyb_minute(records)

        if not desc:
            result.reverse()

        return result

    def _get_next_keyb_minute(self, records: list[dict], period: int = 1) -> str:
        last_record = records[-1]
        last_time: datetime = last_record["stck_cntg_hour"]
        next_time = last_time - timedelta(minutes=period)
        return next_time.strftime("%H%M%S")