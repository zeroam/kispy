"""[해외주식] 기본시세
- 기본적인 시세 정보 조회 (현재가, 호가, 체결, 일별 시세 등)
"""

from datetime import datetime, timedelta

from zoneinfo import ZoneInfo

from kispy.base import BaseAPI
from kispy.constants import ExchangeCode, TimeZoneMap


class QuoteAPI(BaseAPI):
    def get_price(self, symbol: str, exchange_code: ExchangeCode) -> str:
        """해외주식 현재체결가[v1_해외주식-009]

        Args:
            symbol (str): 종목코드
            exchange_code (str): 거래소 코드 (
                HKS : 홍콩, NYS : 뉴욕, NAS : 나스닥, AMS : 아멕스,
                TSE : 도쿄, SHS : 상해, SZS : 심천, SHI : 상해지수,
                SZI : 심천지수, HSX : 호치민, HNX : 하노이,
                BAY : 뉴욕(주간), BAQ : 나스닥(주간), BAA : 아멕스(주간)
            )

        Returns:
            float: 현재체결가

        해외주식 시세는 무료시세(지연체결가)만이 제공되며, API로는 유료시세(실시간체결가)를 받아보실 수 없습니다.

        ※ 지연시세 지연시간 : 미국 - 실시간무료(0분지연) / 홍콩, 베트남, 중국 - 15분지연 / 일본 - 20분지연
        미국의 경우 0분지연시세로 제공되나, 장중 당일 시가는 상이할 수 있으며, 익일 정정 표시됩니다.

        ※ 추후 HTS(efriend Plus) [7781] 시세신청(실시간) 화면에서 유료 서비스 신청 시 실시간 시세 수신할 수 있도록 변경 예정

        ※ 미국주식 시세의 경우 주간거래시간을 제외한 정규장, 애프터마켓, 프리마켓 시간대에 동일한 API(TR)로 시세 조회가 되는 점 유의 부탁드립니다.

        해당 API로 미국주간거래(10:00~16:00) 시세 조회도 가능합니다.
        ※ 미국주간거래 시세 조회 시, EXCD(거래소코드)를 다음과 같이 입력 → 나스닥: BAQ, 뉴욕: BAY, 아멕스: BAA

        ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
        https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

        ​[미국주식시세 이용시 유의사항]
        ■ 무료 실시간 시세(0분 지연) 제공
        ※ 무료(매수/매도 각 10호가) : 나스닥 마켓센터에서 거래되는 호가 및 호가 잔량 정보
        ■ 무료 실시간 시세 서비스는 유료 실시간 시세 서비스 대비 평균 50% 수준에 해당하는 정보이므로
        현재가/호가/순간체결량/차트 등에서 일시적·부분적 차이가 있을 수 있습니다.
        ■ 무료∙유료 모두 미국에 상장된 종목(뉴욕, 나스닥, 아멕스 등)의 시세를 제공하며, 동일한 시스템을 사용하여 주문∙체결됩니다.
        단, 무료∙유료의 기반 데이터 차이로 호가 및 체결 데이터는 차이가 발생할 수 있고, 이로 인해 발생하는 손실에 대해서 당사가 책임지지 않습니다.
        ■ 무료 실시간 시세 서비스의 시가, 저가, 고가, 종가는 유료 실시간 시세 서비스와 다를 수 있으며,
        종목별 과거 데이터(거래량, 시가, 종가, 고가, 차트 데이터 등)는 장 종료 후(오후 12시경) 유료 실시간 시세 서비스 데이터와 동일하게 업데이트됩니다.
        (출처: 한국투자증권 외화증권 거래설명서 - https://www.truefriend.com/main/customer/guide/Guide.jsp?&cmd=TF04ag010002¤tPage=1&num=64)
        """  # noqa: E501
        path = "uapi/overseas-price/v1/quotations/price"
        url = f"{self._url}/{path}"

        headers = self._auth.get_header()
        headers["tr_id"] = "HHDFS00000300"
        params = {
            "AUTH": "",
            "EXCD": exchange_code,
            "SYMB": symbol,
        }

        resp = self._request(method="get", url=url, headers=headers, params=params)
        return resp.json["output"]["last"]  # type: ignore[no-any-return]

    def get_stock_price_history(
        self,
        symbol: str,
        exchange_code: ExchangeCode,
        start_date: str | None = None,
        end_date: str | None = None,
        period: str = "d",
        is_adjust: bool = True,
        desc: bool = False,
        limit: int | None = None,
    ) -> list[dict]:
        """해외주식 기간별시세[v1_해외주식-010]
        https://apiportal.koreainvestment.com/apiservice/apiservice-oversea-stock-quotations#L_0e9fb2ba-bbac-4735-925a-a35e08c9a790

        Args:
            symbol (str): 종목코드
            exchange_code (str): 거래소코드 (
                HKS : 홍콩, NYS : 뉴욕, NAS : 나스닥, AMS : 아멕스, TSE : 도쿄,
                SHS : 상해, SZS : 심천, SHI : 상해지수, SZI : 심천지수, HSX : 호치민, HNX : 하노이,
                BAY : 뉴욕(주간), BAQ : 나스닥(주간), BAA : 아멕스(주간)
            )
            start_date (str): 조회시작일자 (YYYYMMDD)
            end_date (str): 조회종료일자 (YYYYMMDD)
            period (str): 조회기간, 기본값은 "d" (일) (옵션: "d" (일), "w" (주), "M" (월))
            is_adjust (bool): 수정주가 여부, 기본값은 True
            desc (bool): 시간 역순 정렬 여부, 기본값은 False

        Returns:
            list[dict]: 주식 기간별 시세
        """
        period_map = {"d": "0", "w": "1", "M": "2"}
        if period not in period_map:
            raise ValueError(f"Invalid period: {period}")

        path = "uapi/overseas-price/v1/quotations/dailyprice"
        url = f"{self._url}/{path}"

        headers = self._auth.get_header()
        headers["tr_id"] = "HHDFS76240000"

        zone_info = TimeZoneMap[exchange_code]
        parsed_start_date = self._parse_date(start_date, zone_info) if start_date else None
        now = datetime.now(tz=zone_info)
        parsed_end_date = self._parse_date(end_date, zone_info) if end_date else now
        parsed_end_date = min(parsed_end_date, now)

        result: list[dict] = []
        cur_end_date = parsed_end_date
        while cur_end_date >= parsed_start_date if parsed_start_date else True:
            resp = self._request(
                "GET",
                url,
                headers=headers,
                params={
                    "AUTH": "",
                    "EXCD": exchange_code,
                    "SYMB": symbol,
                    "GUBN": period_map[period],
                    "BYMD": cur_end_date.strftime("%Y%m%d"),
                    "MODP": "1" if is_adjust else "0",
                    "KEYB": "",
                },
            )
            items = resp.json["output2"]
            if not items:
                break

            filtered_items = []
            for item in items:
                record_date = self._parse_date(item["xymd"], zone_info)
                if parsed_start_date and record_date < parsed_start_date:
                    continue
                filtered_items.append(item)

            if not filtered_items:
                break

            result.extend(filtered_items)
            cur_end_date = self._parse_date(items[-1]["xymd"], zone_info) - timedelta(days=1)

            if limit and len(result) >= limit:
                result = result[:limit]
                break

        if not desc:
            result.reverse()
        return result

    def get_stock_price_history_by_minute(
        self,
        symbol: str,
        exchange_code: ExchangeCode,
        period: str = "1",
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = 120,
        desc: bool = False,
    ) -> list[dict]:
        """해외주식분봉조회[v1_해외주식-030]
        해외주식분봉조회 API입니다. 실전계좌의 경우, 한 번의 호출에 최근 120건까지 확인 가능합니다.
        NEXT 및 KEYB 값을 사용하여 데이터를 계속해서 다음 조회할 수 있으며, 최대 다음조회 가능 기간은 약 1개월입니다.

        Args:
            symbol (str): 종목코드
            exchange_code (str): 거래소코드
            period (str): 조회기간, 기본값은 "1" (1분)
            start_date (str | None): 조회시작일자 (YYYYMMDD)
            end_date (str | None): 조회종료일자 (YYYYMMDD)
            limit (int | None): 조회건수, 기본값은 120, None일 경우 최대 조회 가능 건수까지 조회

        Returns:
            list[dict]: 주식 분봉 시세
        """
        path = "uapi/overseas-price/v1/quotations/inquire-time-itemchartprice"
        url = f"{self._url}/{path}"

        headers = self._auth.get_header()
        headers["tr_id"] = "HHDFS76950200"

        zone_info = TimeZoneMap[exchange_code]
        now = datetime.now(tz=zone_info)
        parsed_start_date = self._parse_date(start_date, zone_info) if start_date else None
        parsed_end_date = self._parse_date(end_date, zone_info) if end_date else None

        # 먼저 최신 데이터를 한 번 조회하여 마지막 거래 시점 확인
        temp_records = []
        if parsed_end_date:
            temp_records = self._request(
                method="get",
                url=url,
                headers=headers,
                params={
                    "AUTH": "",
                    "EXCD": exchange_code,
                    "SYMB": symbol,
                    "NMIN": period,
                    "PINC": "1",
                    "NEXT": "",
                    "NREC": "1",
                    "FILL": "",
                    "KEYB": "",
                },
            ).json["output2"]

            latest_record = temp_records[0]
            latest_time = self._parse_date(latest_record["xymd"] + latest_record["xhms"], zone_info)
            if parsed_end_date >= latest_time:
                next_value = ""
                keyb = ""
            else:
                next_value = "1"
                keyb = parsed_end_date.strftime("%Y%m%d%H%M%S")
        else:
            next_value = "1"
            keyb = now.strftime("%Y%m%d%H%M%S")

        result: list[dict] = []
        while limit is None or len(result) < limit:
            size = min(limit - len(result), 120) if limit else 120
            params = {
                "AUTH": "",
                "EXCD": exchange_code,
                "SYMB": symbol,
                "NMIN": period,
                "PINC": "1",
                "NEXT": next_value,
                "NREC": str(size),
                "FILL": "",
                "KEYB": keyb,
            }

            resp = self._request(method="get", url=url, headers=headers, params=params)
            records = resp.json["output2"]
            if not records:
                break

            filtered_records = []
            for record in records:
                record_date = self._parse_date(record["xymd"] + record["xhms"], zone_info)
                if parsed_start_date and record_date < parsed_start_date:
                    continue
                filtered_records.append(record)

            if not filtered_records:
                break

            result.extend(filtered_records)

            keyb = self._get_next_keyb(records, period)
            next_value = resp.json["output1"]["next"]
            if next_value == "0":
                break

        if not desc:
            result.reverse()
        return result

    def _get_next_keyb(self, items: list[dict], period: str) -> str:
        last_record = items[-1]
        last_time_str = last_record["xymd"] + last_record["xhms"]
        last_time = datetime.strptime(last_time_str, "%Y%m%d%H%M%S")
        next_time = last_time - timedelta(minutes=int(period))
        return next_time.strftime("%Y%m%d%H%M%S")