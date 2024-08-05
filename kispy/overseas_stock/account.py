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

import requests

from kispy.auth import AuthAPI
from kispy.constants import REAL_URL, VIRTUAL_URL
from kispy.responses import BaseResponse


class AccountAPI:
    def __init__(self, auth: AuthAPI):
        self._url = REAL_URL if auth.is_real else VIRTUAL_URL
        self._auth = auth

    def _request(self, method: str, url: str, **kwargs) -> BaseResponse:
        resp = requests.request(method, url, **kwargs)
        custom_resp = BaseResponse(status_code=resp.status_code, json=resp.json())
        custom_resp.raise_for_status()
        return custom_resp

    def inquire_balance(self) -> dict:
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
        query = {
            "CANO": self._auth.cano,
            "ACNT_PRDT_CD": self._auth.acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 나스닥
            "TR_CRCY_CD": "USD",  # 미국달러
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": "",
        }

        resp = self._request(method="get", url=url, headers=headers, params=query)
        return resp.json
