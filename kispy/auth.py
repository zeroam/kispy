import logging
import os
import pickle
import tempfile
from datetime import datetime

import pytz
import requests
from pydantic import BaseModel, Field

from kispy.constants import REAL_URL, VIRTUAL_URL
from kispy.responses import AuthResponse

logger = logging.getLogger(__name__)


class Token(BaseModel):
    access_token: str = Field(description="액세스 토큰")
    token_type: str = "Bearer"
    expires_in: int = Field(description="접근 토큰 유효기간")
    access_token_token_expired: datetime = Field(description="액세스 토큰 만료일시")

    def is_expired(self) -> bool:
        kst = pytz.timezone("Asia/Seoul")
        return datetime.now(kst) > self.access_token_token_expired


class KisAuth:
    def __init__(
        self,
        app_key: str,
        secret: str,
        account_no: str,
        is_real: bool,
    ):
        self._url = REAL_URL if is_real else VIRTUAL_URL
        self.app_key = app_key
        self.app_secret = secret
        self.is_real = is_real
        self.cano, self.acnt_prdt_cd = account_no.split("-")
        self._token: Token | None = None
        self._file_path = os.path.join(tempfile.gettempdir(), f"kis_{self.app_key}")

    def _request(self, method: str, url: str, **kwargs) -> AuthResponse:
        resp = requests.request(method, url, **kwargs)
        custom_resp = AuthResponse(headers=dict(resp.headers), status_code=resp.status_code, json=resp.json())
        custom_resp.raise_for_status()
        return custom_resp

    def _get_token(self) -> Token:
        url = f"{self._url}/oauth2/tokenP"
        resp = self._request(
            "POST",
            url,
            json={
                "grant_type": "client_credentials",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
            },
        )
        kst = pytz.timezone("Asia/Seoul")
        access_token_token_expired = kst.localize(
            datetime.strptime(
                resp.json["access_token_token_expired"],
                "%Y-%m-%d %H:%M:%S",
            )
        ).replace(tzinfo=kst)
        return Token(
            token_type=resp.json["token_type"],
            access_token=resp.json["access_token"],
            expires_in=int(resp.json["expires_in"]),
            access_token_token_expired=access_token_token_expired,
        )

    @property
    def access_token(self) -> str:
        logger.debug(f"access_token: {self._token}")
        if self._token is not None and not self._token.is_expired():
            return self._token.access_token

        token: Token | None = None
        if os.path.exists(self._file_path):
            logger.debug("load token from pickle")
            with open(self._file_path, "rb") as f:
                token = pickle.load(f)
                logger.debug(f"loaded token: {token}")

        if token is None or token.is_expired():
            logger.debug("get new token")
            token = self._get_token()
            with open(self._file_path, "wb") as f:
                pickle.dump(token, f)
            logger.debug(f"saved token: {token}")

        self._token = token
        return self._token.access_token

    def get_header(self) -> dict:
        return {
            "content-type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
        }
