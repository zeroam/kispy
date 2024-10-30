"""[해외주식] 주문/계좌
- 해외주식 주문
- 해외주식 정정취소주문
- 해외주식 예약주문
- 해외주식 예약주문취소
- 해외주식 미체결내역
- 해외주식 주문체결내역
"""

import requests

from kispy.auth import KisAuth
from kispy.constants import REAL_URL, VIRTUAL_URL
from kispy.responses import BaseResponse


class OrderAPI:
    def __init__(self, auth: KisAuth):
        self._url = REAL_URL if auth.is_real else VIRTUAL_URL
        self._auth = auth

    def _request(self, method: str, url: str, **kwargs) -> BaseResponse:
        resp = requests.request(method, url, **kwargs)
        custom_resp = BaseResponse(status_code=resp.status_code, json=resp.json())
        custom_resp.raise_for_status()
        return custom_resp

    def buy(self, symbol: str, exchange: str, quantity: int, price: float) -> dict:
        """해외주식주문[v1_해외주식-001] - 매수

        해외주식 주문 API입니다.

        * 모의투자의 경우, 모든 해외 종목 매매가 지원되지 않습니다. 일부 종목만 매매 가능한 점 유의 부탁드립니다.

        * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

        * 해외 거래소 운영시간 외 API 호출 시 애러가 발생하오니 운영시간을 확인해주세요.
        * 해외 거래소 운영시간(한국시간 기준)
        1) 미국 : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)
        2) 일본 : (오전) 09:00 ~ 11:30, (오후) 12:30 ~ 15:00
        3) 상해 : 10:30 ~ 16:00
        4) 홍콩 : (오전) 10:30 ~ 13:00, (오후) 14:00 ~ 17:00

        ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
        (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)

        ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
        https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info


        - 주문단가와 체결 단가는 다를 수 있음
        """
        # 현재는 미국 매수만 가능
        path = "uapi/overseas-stock/v1/trading/order"
        url = f"{self._url}/{path}"

        tr_id = _get_buy_tr_id(exchange, self._auth.is_real)

        headers = self._auth.get_header()
        headers["tr_id"] = tr_id
        # TODO: symbol에 따라서 OVRS_EXCG_CD를 결정해야 함
        body = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 나스닥
            "PDNO": symbol,
            "ORD_QTY": str(quantity),
            "OVRS_ORD_UNPR": str(price),
            "ORD_SVR_DVSN_CD": "0",  # Default
            "ORD_DVSN": "00",  # 매수 00: 지정가, 32: LOO(장개시지정가), 34: LOC(장마감지정가)
        }

        resp = self._request(method="post", url=url, headers=headers, json=body)
        # TODO: resp 타입 정의하기
        return resp.json["output"]  # type: ignore[no-any-return]

    def buy_market(self, symbol: str, exchange: str, quantity: int) -> dict:
        return self.buy(symbol, exchange, quantity, 0)

    def sell(self, symbol: str, exchange: str, quantity: int, price: float) -> dict:
        """해외주식주문[v1_해외주식-001] - 매도

        해외주식 주문 API입니다.

        * 모의투자의 경우, 모든 해외 종목 매매가 지원되지 않습니다. 일부 종목만 매매 가능한 점 유의 부탁드립니다.

        * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

        * 해외 거래소 운영시간 외 API 호출 시 애러가 발생하오니 운영시간을 확인해주세요.
        * 해외 거래소 운영시간(한국시간 기준)
        1) 미국 : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)
        2) 일본 : (오전) 09:00 ~ 11:30, (오후) 12:30 ~ 15:00
        3) 상해 : 10:30 ~ 16:00
        4) 홍콩 : (오전) 10:30 ~ 13:00, (오후) 14:00 ~ 17:00

        ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
        (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)

        ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
        https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
        """
        # 현재는 미국 매도만 가능
        path = "uapi/overseas-stock/v1/trading/order"
        url = f"{self._url}/{path}"

        headers = self._auth.get_header()
        headers["tr_id"] = _get_sell_tr_id(exchange, self._auth.is_real)
        body = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 나스닥
            "PDNO": symbol,
            "ORD_QTY": str(quantity),
            "OVRS_ORD_UNPR": str(price),
            "ORD_SVR_DVSN_CD": "0",  # Default
            "SLL_TYPE": "00",  # 판매유형: 00-매도
            "ORD_DVSN": "00",  # 매수 00: 지정가, 32: LOO(장개시지정가), 34: LOC(장마감지정가)
        }

        resp = self._request(method="post", url=url, headers=headers, json=body)
        return resp.json["output"]  # type: ignore[no-any-return]

    def sell_market(self, symbol: str, exchange: str, quantity: int) -> dict:
        return self.sell(symbol, exchange, quantity, 0)

    def update(
        self,
        symbol: str,
        order_number: str,
        quantity: str,
        price: float,
    ) -> dict:
        """
        해외주식 정정취소주문[v1_해외주식-003] - 정정

        - 2개 주문하고 1개만 수정하면? 수량 불일치 에러, 수량을 맞춰야 함
        """
        path = "uapi/overseas-stock/v1/trading/order-rvsecncl"
        url = f"{self._url}/{path}"

        if self._auth.is_real:
            tr_id = "TTTT1004U"
        else:
            tr_id = "VTTT1004U"

        headers = self._auth.get_header()
        headers["tr_id"] = tr_id
        body = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 나스닥
            "PDNO": symbol,
            "ORGN_ODNO": order_number,
            "RVSE_CNCL_DVSN_CD": "01",  # 정정
            "ORD_QTY": str(quantity),
            "OVRS_ORD_UNPR": str(price),  # 해외주문단가
        }

        resp = self._request(method="post", url=url, headers=headers, json=body)
        return resp.json["output"]  # type: ignore[no-any-return]

    def cancel(self, symbol: str, order_number: str) -> dict:
        """
        해외주식 정정취소주문[v1_해외주식-003] - 취소

        # 2개 주문하고 1개만 취소하면? 취소는 수량 관계없이 가능
        """
        path = "uapi/overseas-stock/v1/trading/order-rvsecncl"
        url = f"{self._url}/{path}"

        if self._auth.is_real:
            tr_id = "TTTT1004U"
        else:
            tr_id = "VTTT1004U"

        headers = self._auth.get_header()
        headers["tr_id"] = tr_id
        body = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 나스닥
            "PDNO": symbol,
            "ORGN_ODNO": order_number,
            "RVSE_CNCL_DVSN_CD": "02",  # 취소
            "ORD_QTY": "1",  # 취소주문수량, 취소 주문은 수량 관계 없이 거래 취소
            "OVRS_ORD_UNPR": "0",  # 해외주문단가, 취소주문시 0
        }

        resp = self._request(method="post", url=url, headers=headers, json=body)
        return resp.json["output"]  # type: ignore[no-any-return]

    def inquire_outstanding_orders(self) -> dict:
        """
        해외주식 미체결내역[v1_해외주식-005]

        - 한번 호출에 40개 그 이후 조회는 FK, NK를 활용한 구현 필요
        """
        path = "uapi/overseas-stock/v1/trading/inquire-nccs"
        url = f"{self._url}/{path}"

        if self._auth.is_real:
            tr_id = "TTTS3018R"
        else:
            tr_id = "VTTS3018R"

        headers = self._auth.get_header()
        headers["tr_id"] = tr_id
        params = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 나스닥
            "SORT_SQN": "DS",  # 정렬순서: DS-내림차순, AS-오름차순
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": "",
        }

        resp = self._request(method="get", url=url, headers=headers, params=params)
        return resp.json

    def inquire_executed_orders(self, start_date: str, end_date: str) -> dict:
        """해외주식 주문체결내역[v1_해외주식-007]

        일정 기간의 해외주식 주문 체결 내역을 확인하는 API입니다.
        실전계좌의 경우, 한 번의 호출에 최대 20건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
        모의계좌의 경우, 한 번의 호출에 최대 15건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.

        * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

        ※ 해외 거래소 운영시간(한국시간 기준)
        1) 미국 : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)
        2) 일본 : (오전) 09:00 ~ 11:30, (오후) 12:30 ~ 15:00
        3) 상해 : 10:30 ~ 16:00
        4) 홍콩 : (오전) 10:30 ~ 13:00, (오후) 14:00 ~ 17:00
        """
        path = "uapi/overseas-stock/v1/trading/inquire-ccnl"
        url = f"{self._url}/{path}"

        if self._auth.is_real:
            tr_id = "TTTS3035R"
        else:
            tr_id = "VTTS3035R"

        headers = self._auth.get_header()
        headers["tr_id"] = tr_id
        params = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "PDNO": "%",  # 상품번호, 전종목일 경우 % 입력
            "ORD_STRT_DT": start_date,  # 조회시작일자
            "ORD_END_DT": end_date,  # 조회종료일자
            "SLL_BUY_DVSN": "00",  # 매도매수구분: 00-전체, 01-매도, 02-매수
            "CCLD_NCCS_DVSN": "00",  # 체결미체결구분: 00-전체, 01-체결, 02-미체결
            "OVRS_EXCG_CD": "NASD",  # 거래소코드: NASD-나스닥, NYSE-뉴욕증권거래소, ...
            "SORT_SQN": "DS",  # 정렬순서: DS-내림차순, AS-오름차순
            "ORD_DT": "",
            "ORD_GNO_BRNO": "",
            "ODNO": "",
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": "",
        }

        resp = self._request(method="get", url=url, headers=headers, params=params)
        return resp.json


def _get_buy_tr_id(exchange: str, is_real: bool) -> str:
    real_tr_id = {
        "NASD": "TTTT1002U",
        "NYSE": "TTTT1002U",
        "AMEX": "TTTT1002U",
        "SEHK": "TTTS1002U",
        "SHAA": "TTTS0202U",
        "SZAA": "TTTS0305U",
        "TKSE": "TTTS0308U",
        "HASE": "TTTS0311U",
        "VNSE": "TTTS0311U",
    }

    mock_tr_id = {
        "NASD": "VTTT1002U",
        "NYSE": "VTTT1002U",
        "AMEX": "VTTT1002U",
        "SEHK": "VTTS1002U",
        "SHAA": "VTTS0202U",
        "SZAA": "VTTS0305U",
        "TKSE": "VTTS0308U",
        "HASE": "VTTS0311U",
        "VNSE": "VTTS0311U",
    }

    if is_real:
        return real_tr_id[exchange]
    else:
        return mock_tr_id[exchange]


def _get_sell_tr_id(exchange: str, is_real: bool) -> str:
    real_tr_id = {
        "NASD": "TTTT1006U",
        "NYSE": "TTTT1006U",
        "AMEX": "TTTT1006U",
        "SEHK": "TTTS1001U",
        "SHAA": "TTTS1005U",
        "SZAA": "TTTS0304U",
        "TKSE": "TTTS0307U",
        "HASE": "TTTS0310U",
        "VNSE": "TTTS0310U",
    }

    mock_tr_id = {
        "NASD": "VTTT1006U",
        "NYSE": "VTTT1006U",
        "AMEX": "VTTT1006U",
        "SEHK": "VTTS1001U",
        "SHAA": "VTTS1005U",
        "SZAA": "VTTS0304U",
        "TKSE": "VTTS0307U",
        "HASE": "VTTS0310U",
        "VNSE": "VTTS0310U",
    }

    if is_real:
        return real_tr_id[exchange]
    else:
        return mock_tr_id[exchange]
