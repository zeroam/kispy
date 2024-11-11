"""[해외주식] 주문/계좌
- 해외주식 잔고
- 해외주식 매수가능금액
- 해외주식 체결기준현재잔고
- 해외주식 체결기준잔고유효종목
- 해외주식 예약주문조회
- 해외주식 매수가능종목조회
- 해외주식 일별손익현황
- 해외주식 결제기준잔고현재잔고
- 해외주식 최대주문가능수량조회
- 해외주식 일괄주문조회
- 해외증거금 통화별조회
"""

from kispy.base import BaseAPI
from kispy.constants import Currency, LongExchangeCode
from kispy.exceptions import InvalidAccount


class AccountAPI(BaseAPI):
    def inquire_nccs(self, exchange_code: LongExchangeCode, desc: bool = False) -> dict:
        """해외주식 미체결내역[v1_해외주식-005]

        Args:
            exchange_code (LongExchangeCode): 거래소코드
            desc (bool): 시간 역순 정렬 여부, 기본값은 False

        Returns:
            dict: 미체결내역

        접수된 해외주식 주문 중 체결되지 않은 미체결 내역을 조회하는 API입니다.
        실전계좌의 경우, 한 번의 호출에 최대 40건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.

        * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

        ※ 해외 거래소 운영시간(한국시간 기준)
        1) 미국 : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)
        2) 일본 : (오전) 09:00 ~ 11:30, (오후) 12:30 ~ 15:00
        3) 상해 : 10:30 ~ 16:00
        4) 홍콩 : (오전) 10:30 ~ 13:00, (오후) 14:00 ~ 17:00
        """
        path = "uapi/overseas-stock/v1/trading/inquire-nccs"
        url = f"{self._url}/{path}"

        headers = self._auth.get_header()
        tr_id = "TTTS3018R" if self._auth.is_real else "VTTS3018R"
        headers["tr_id"] = tr_id

        # TODO: 40개 이상 조회 지원
        params = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "OVRS_EXCG_CD": exchange_code,
            "SORT_SQN": "" if desc else "DS",
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": "",
        }

        resp = self._request(method="get", url=url, headers=headers, params=params)
        return resp.json["output"]  # type: ignore[no-any-return]

    def inquire_balance(self, exchange_code: LongExchangeCode, currency: Currency) -> dict:
        """해외주식 잔고[v1_해외주식-006]

        해외주식 잔고를 조회하는 API 입니다.
        한국투자 HTS(eFriend Plus) > [7600] 해외주식 종합주문 화면의 좌측 하단 '실시간잔고' 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
        다만 미국주간거래 가능종목에 대해서는 frcr_evlu_pfls_amt(외화평가손익금액), evlu_pfls_rt(평가손익율), ovrs_stck_evlu_amt(해외주식평가금액), now_pric2(현재가격2) 값이 HTS와는 상이하게 표출될 수 있습니다.
        (주간시간 시간대에 HTS는 주간시세로 노출, API로는 야간시세로 노출)

        실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.

        * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

        * 미니스탁 잔고는 해당 API로 확인이 불가합니다.
        """  # noqa: E501
        path = "uapi/overseas-stock/v1/trading/inquire-balance"
        url = f"{self._url}/{path}"

        if self._auth.is_real:
            tr_id = "TTTS3012R"  # 실전투자
        else:
            tr_id = "VTTS3012R"

        headers = self._auth.get_header()
        headers["tr_id"] = tr_id
        # TODO: 100개 이상 조회 지원
        params = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "OVRS_EXCG_CD": exchange_code,
            "TR_CRCY_CD": currency,
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": "",
        }

        resp = self._request(method="get", url=url, headers=headers, params=params)
        return resp.json

    def inquire_order_resv_list(self, start_date: str, end_date: str, division_code: str = "01") -> dict:
        """해외주식 예약주문조회[v1_해외주식-013]"""
        path = "uapi/overseas-stock/v1/trading/order-resv-list"
        url = f"{self._url}/{path}"

        tr_id = "TTTT3039R"  # TODO: 미국, 다른 국가 지원 필요
        headers = self._auth.get_header()
        headers["tr_id"] = tr_id

        params = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "INQR_STRT_DT": start_date,  # 조회시작일자
            "INQR_END_DT": end_date,  # 조회종료일자
            "INQR_DVSN_CD": division_code,  # 조회구분코드 (00: 전체, 01: 일반해외주식, 02: 미니스탁)
            "PRDT_TYPE_CD": "",  # 상품유형코드
            "OVRS_EXCG_CD": "",  # 거래소코드
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": "",
        }

        resp = self._request(method="get", url=url, headers=headers, params=params)
        return resp.json

    def inquire_psamount(self, symbol: str, exchange_code: LongExchangeCode) -> dict:
        """해외주식 매수가능금액조회[v1_해외주식-014]
        해외주식 매수가능금액조회 API입니다.

        * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고) https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
        """
        path = "uapi/overseas-stock/v1/trading/inquire-psamount"
        url = f"{self._url}/{path}"

        if self._auth.is_real:
            tr_id = "TTTS3007R"  # 실전투자
        else:
            tr_id = "VTTS3007R"

        headers = self._auth.get_header()
        headers["tr_id"] = tr_id
        query = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "OVRS_EXCG_CD": exchange_code,
            "OVRS_ORD_UNPR": "",
            "ITEM_CD": symbol,
        }

        resp = self._request(method="get", url=url, headers=headers, params=query)
        return resp.json["output"]  # type: ignore[no-any-return]

    def inquire_payment_standard_balance(self, base_date: str, is_krw: bool = True, division_code: str = "00") -> dict:
        """해외주식 결제기준잔고 [해외주식-064]

        Args:
            base_date (str): 기준일자 (YYYYMMDD)
            is_krw (bool): 원화외화구분코드
            division_code (str): 조회구분코드 (00: 전체, 01: 일반, 02: 미니스탁)

        해외주식 결제기준잔고 API입니다.
        한국투자 HTS(eFriend Plus) > [0829] 해외 결제기준잔고 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

        ※ 적용환율은 당일 매매기준이며, 현재가의 경우 지연된 시세로 평가되므로 실제매도금액과 상이할 수 있습니다.
        ※ 주문가능수량 : 보유수량 - 미결제 매도수량
        ※ 매입금액 계산 시 결제일의 최초고시환율을 적용하므로, 금일 최초고시환율을 적용하는 체결기준 잔고와는 상이합니다.
        ※ 해외증권 투자 및 업무문의 안내: 한국투자증권 해외투자지원부 02)3276-5300
        """  # noqa: E501
        if not self._auth.is_real:
            raise InvalidAccount("실전계좌만 사용 가능합니다.")

        path = "uapi/overseas-stock/v1/trading/inquire-paymt-stdr-balance"
        url = f"{self._url}/{path}"

        tr_id = "CTRP6010R"

        headers = self._auth.get_header()
        headers["tr_id"] = tr_id
        query = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "BASS_DT": base_date,
            "WCRC_FRCR_DVSN_CD": "01" if is_krw else "02",
            "INQR_DVSN_CD": division_code,
        }

        resp = self._request(method="get", url=url, headers=headers, params=query)
        return resp.json
