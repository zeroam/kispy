import logging
import os
import pickle
from datetime import datetime

import requests

from kispy.auth import Auth, Token
from kispy.response import Response

logger = logging.getLogger(__name__)


class KisClient:
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        account_no: str,
        is_real: bool = False,
        auth_cls: type[Auth] = Token,
    ) -> None:
        """KIS API 클라이언트를 초기화합니다.

        Args:
            app_key (str): 한국투자증권에서 발급받은 앱키
            app_secret (str): 한국투자증권에서 발급받은 앱시크릿
            account_no (str): 사용할 계좌번호 (예: "5000000000-01")
            is_real (bool, optional): 실전투자 여부. 기본값은 False (모의투자).
            auth_cls (type[Auth], optional): 사용할 인증 클래스. 기본값은 Token.

        Note:
            account_no는 "계좌번호-상품코드" 형식으로 입력해야 합니다.

        Raises:
            ValueError: account_no가 올바른 형식이 아닐 경우 발생

        Example:
            >>> client = KISClient("your_app_key", "your_app_secret", "5000000000-01")
        """
        if is_real:
            self.url = "https://openapi.koreainvestment.com:9443"  # 실전투자 API
        else:
            self.url = "https://openapivts.koreainvestment.com:29443"  # 모의투자 API
        self._app_key = app_key
        self._app_secret = app_secret
        self._cano, self._acnt_prdt_cd = account_no.split("-")
        self._is_real = is_real
        self._auth_cls = auth_cls
        self._token: Token | None = None
        self._pickle_path = f"kis_{self._cano}.pickle"

    def _request(self, method: str, url: str, **kwargs) -> Response:
        resp = requests.request(method, url, **kwargs)
        custom_resp = Response(resp)
        custom_resp.raise_for_status()
        return custom_resp

    def _get_token(self) -> Token:
        path = "oauth2/tokenP"
        url = f"{self.url}/{path}"
        body = {
            "grant_type": "client_credentials",
            "appkey": self._app_key,
            "appsecret": self._app_secret,
        }

        resp = self._request(method="post", url=url, json=body)
        body = resp.body
        access_token_token_expired = datetime.strptime(
            body["access_token_token_expired"],
            "%Y-%m-%d %H:%M:%S",
        )
        return Token(
            token_type=body["token_type"],
            access_token=body["access_token"],
            expires_in=int(body["expires_in"]),
            access_token_token_expired=access_token_token_expired,
        )

    @property
    def access_token(self):
        if self._token is not None and not self._token.is_expired():
            return self._token.access_token

        token: Token | None = None

        if os.path.exists(self._pickle_path):
            logger.debug("load token from pickle")
            with open(self._pickle_path, "rb") as f:
                token = pickle.load(f)
                logger.debug(f"loaded token: {token}")

        if token is None or token.is_expired():
            logger.debug("get new token")
            token = self._get_token()
            with open(self._pickle_path, "wb") as f:
                pickle.dump(token, f)
            logger.debug(f"saved token: {token}")

        self._token = token
        return self._token.access_token

    def get_domestic_stock_price(self, code: str) -> int:
        """
        주식 현재가 시세 API입니다. 실시간 시세를 원하신다면 웹소켓 API를 활용하세요.

        Args:
            code (str): 종목코드

        Returns:
            int: 주식 현재가
        """
        path = "uapi/domestic-stock/v1/quotations/inquire-price"
        url = f"{self.url}/{path}"

        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "tr_id": "FHKST01010100",
            "appKey": self._app_key,
            "appSecret": self._app_secret,
        }
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": code,
        }

        resp = self._request(method="get", url=url, headers=headers, params=params)
        return int(resp.body["output"]["stck_prpr"])

    def buy_domestic_stock(self, stock_code: str, quantity: int, price: float) -> dict:
        """
        주식주문(현금)[v1_국내주식-001] - 매수
        """
        path = "uapi/domestic-stock/v1/trading/order-cash"
        url = f"{self.url}/{path}"

        if self._is_real:
            tr_id = "TTTC0802U"  # 실전투자
        else:
            tr_id = "VTTC0802U"  # 모의투자

        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self._app_key,
            "appsecret": self._app_secret,
            "tr_id": tr_id,
        }
        params = {
            "CANO": self._cano,
            "ACNT_PRDT_CD": self._acnt_prdt_cd,
            "PDNO": stock_code,
            "ORD_DVSN": "00",  # 주문구분: 00-지정가, 01-시장가
            "ORD_QTY": str(quantity),  # 주문수량
            "ORD_UNPR": str(price),
        }

        resp = self._request(method="post", url=url, headers=headers, json=params)
        return resp.body

    def sell_domestic_stock(self) -> dict:
        """
        주식주문(현금)[v1_국내주식-001] - 매도
        """
        return {}

    def get_overseas_inquire_balance(self) -> dict:
        """
        해외주식 잔고[v1_해외주식-006]

        - 잔고가 있는데 왜 조회가 안되지?
        """
        path = "uapi/overseas-stock/v1/trading/inquire-balance"
        url = f"{self.url}/{path}"

        if self._is_real:
            tr_id = "TTTS3012R"  # 실전투자
        else:
            tr_id = "VTTS3012R"

        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "tr_id": tr_id,
            "appkey": self._app_key,
            "appsecret": self._app_secret,
        }
        query = {
            "CANO": self._cano,
            "ACNT_PRDT_CD": self._acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 나스닥
            "TR_CRCY_CD": "USD",  # 미국달러
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": "",
        }

        resp = self._request(method="get", url=url, headers=headers, params=query)
        return resp.body

    def get_overseas_inquire_psamount(self, code: str, price: float) -> dict:
        """
        해외주식 매수가능금액조회[v1_해외주식-014]

        - FIXME: 이게 왜 필요하지?
        """
        path = "uapi/overseas-stock/v1/trading/inquire-psamount"
        url = f"{self.url}/{path}"

        if self._is_real:
            tr_id = "TTTS3007R"
        else:
            tr_id = "VTTS3007R"

        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "tr_id": tr_id,
            "appkey": self._app_key,
            "appsecret": self._app_secret,
        }
        params = {
            "CANO": self._cano,
            "ACNT_PRDT_CD": self._acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 나스닥
            "OVRS_ORD_UNPR": str(price),  # 해외주식주문단가
            "ITEM_CD": code,
        }

        resp = self._request(method="get", url=url, headers=headers, params=params)
        return resp.body

    def get_overseas_stock_price(self, code: str) -> dict:
        """
        해외주식 현재체결가[v1_해외주식-009]
        """
        path = "uapi/overseas-price/v1/quotations/price"
        url = f"{self.url}/{path}"

        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self._app_key,
            "appsecret": self._app_secret,
            "tr_id": "HHDFS00000300",
        }
        params = {
            "AUTH": "",
            "EXCD": "NAS",  # 나스닥
            "SYMB": code,
        }

        resp = self._request(method="get", url=url, headers=headers, params=params)
        # TODO: resp 타입 정의하기
        return float(resp.body["output"]["last"])  # type: ignore[return-value]

    def buy_overseas_stock(self, code: str, quantity: int, price: float) -> None:
        """
        해외주식주문[v1_해외주식-001] - 매수

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
        url = f"{self.url}/{path}"

        if self._is_real:
            tr_id = "TTTT1002U"  # 실전투자
        else:
            tr_id = "VTTT1002U"  # 모의투자

        body = {
            "CANO": self._cano,
            "ACNT_PRDT_CD": self._acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 나스닥
            "PDNO": code,
            "ORD_QTY": str(quantity),
            "OVRS_ORD_UNPR": str(price),
            "ORD_SVR_DVSN_CD": "0",  # Default
            "ORD_DVSN": "00",  # 매수 00: 지정가, 32: LOO(장개시지정가), 34: LOC(장마감지정가)
        }
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self._app_key,
            "appsecret": self._app_secret,
            "tr_id": tr_id,
        }

        resp = self._request(method="post", url=url, headers=headers, json=body)
        # TODO: resp 타입 정의하기
        return resp.body["output"]  # type: ignore[no-any-return]

    def sell_overseas_stock(self, code: str, quantity: int, price: float) -> dict:
        """
        해외주식주문[v1_해외주식-001] - 매도
        """
        # 현재는 미국 매도만 가능
        path = "uapi/overseas-stock/v1/trading/order"
        url = f"{self.url}/{path}"

        if self._is_real:
            tr_id = "TTTT1006U"  # 실전투자
        else:
            tr_id = "VTTT1006U"  # 모의투자

        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self._app_key,
            "appsecret": self._app_secret,
            "tr_id": tr_id,
        }
        body = {
            "CANO": self._cano,
            "ACNT_PRDT_CD": self._acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 나스닥
            "PDNO": code,
            "ORD_QTY": str(quantity),
            "OVRS_ORD_UNPR": str(price),
            "ORD_SVR_DVSN_CD": "0",  # Default
            "SLL_TYPE": "00",  # 판매유형: 00-매도
            "ORD_DVSN": "00",  # 매수 00: 지정가, 32: LOO(장개시지정가), 34: LOC(장마감지정가)
        }

        resp = self._request(method="post", url=url, headers=headers, json=body)
        return resp.body["output"]  # type: ignore[no-any-return]

    def update_overseas_stock(
        self,
        code: str,
        order_number: str,
        quantity: int,
        price: float,
    ) -> dict:
        """
        해외주식 정정취소주문[v1_해외주식-003] - 정정

        - 2개 주문하고 1개만 수정하면? 수량 불일치 에러, 수량을 맞춰야 함
        """
        path = "uapi/overseas-stock/v1/trading/order-rvsecncl"
        url = f"{self.url}/{path}"

        if self._is_real:
            tr_id = "TTTT1004U"
        else:
            tr_id = "VTTT1004U"

        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self._app_key,
            "appsecret": self._app_secret,
            "tr_id": tr_id,
        }
        body = {
            "CANO": self._cano,
            "ACNT_PRDT_CD": self._acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 나스닥
            "PDNO": code,
            "ORGN_ODNO": order_number,
            "RVSE_CNCL_DVSN_CD": "01",  # 정정
            "ORD_QTY": str(quantity),
            "OVRS_ORD_UNPR": str(price),  # 해외주문단가
        }

        resp = self._request(method="post", url=url, headers=headers, json=body)
        return resp.body["output"]  # type: ignore[no-any-return]

    def cancel_overseas_stock(
        self,
        code: str,
        order_number: str,
    ) -> dict:
        """
        해외주식 정정취소주문[v1_해외주식-003] - 취소

        # 2개 주문하고 1개만 취소하면? 취소는 수량 관계없이 가능
        """
        path = "uapi/overseas-stock/v1/trading/order-rvsecncl"
        url = f"{self.url}/{path}"

        if self._is_real:
            tr_id = "TTTT1004U"
        else:
            tr_id = "VTTT1004U"

        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self._app_key,
            "appsecret": self._app_secret,
            "tr_id": tr_id,
        }
        body = {
            "CANO": self._cano,
            "ACNT_PRDT_CD": self._acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 나스닥
            "PDNO": code,
            "ORGN_ODNO": order_number,
            "RVSE_CNCL_DVSN_CD": "02",  # 취소
            "ORD_QTY": "1",  # 취소주문수량, 취소 주문은 수량 관계 없이 거래 취소
            "OVRS_ORD_UNPR": "0",  # 해외주문단가, 취소주문시 0
        }

        resp = self._request(method="post", url=url, headers=headers, json=body)
        return resp.body["output"]  # type: ignore[no-any-return]

    def get_unexecuted_order(self) -> dict:
        """
        해외주식 미체결내역[v1_해외주식-005]

        - 한번 호출에 40개 그 이후 조회는 FK, NK를 활용한 구현 필요
        """
        path = "uapi/overseas-stock/v1/trading/inquire-nccs"
        url = f"{self.url}/{path}"

        if self._is_real:
            tr_id = "TTTS3018R"
        else:
            tr_id = "VTTS3018R"

        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self._app_key,
            "appsecret": self._app_secret,
            "tr_id": tr_id,
        }
        params = {
            "CANO": self._cano,
            "ACNT_PRDT_CD": self._acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 나스닥
            "SORT_SQN": "DS",  # 정렬순서: DS-내림차순, AS-오름차순
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": "",
        }

        resp = self._request(method="get", url=url, headers=headers, params=params)
        return resp.body

    def get_executed_order(self) -> None:
        """
        해외주식 주문체결내역[v1_해외주식-007]
        """
        pass
