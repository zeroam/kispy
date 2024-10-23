import logging

import requests

from kispy.auth import AuthAPI
from kispy.constants import REAL_URL, VIRTUAL_URL
from kispy.domestic_stock import DomesticStock
from kispy.overseas_stock import OverseasStock
from kispy.responses import BaseResponse

logger = logging.getLogger(__name__)


class KisClient:
    def __init__(
        self,
        auth: AuthAPI,
    ) -> None:
        """KIS API 클라이언트를 초기화합니다.

        Args:
            app_key (str): 한국투자증권에서 발급받은 앱키
            app_secret (str): 한국투자증권에서 발급받은 앱시크릿
            account_no (str): 사용할 계좌번호 (예: "5000000000-01")
            is_real (bool, optional): 실전투자 여부. 기본값은 False (모의투자).

        Note:
            account_no는 "계좌번호-상품코드" 형식으로 입력해야 합니다.

        Raises:
            ValueError: account_no가 올바른 형식이 아닐 경우 발생

        Example:
            >>> client = KISClient("your_app_key", "your_app_secret", "5000000000-01")
        """
        self._url = REAL_URL if auth.is_real else VIRTUAL_URL
        self._auth = auth
        self.domestic_stock = DomesticStock(auth=self._auth)
        self.overseas_stock = OverseasStock(auth=self._auth)

    def _request(self, method: str, url: str, **kwargs) -> BaseResponse:
        resp = requests.request(method, url, **kwargs)
        custom_resp = BaseResponse(status_code=resp.status_code, json=resp.json())
        custom_resp.raise_for_status()
        return custom_resp
