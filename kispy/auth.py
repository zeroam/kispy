from datetime import datetime

from pydantic import BaseModel, Field


class Auth(BaseModel):
    """
    인증 방식을 정의하는 클래스
    """

    pass


class Token(Auth):
    access_token: str = Field(description="액세스 토큰")
    token_type: str = "Bearer"
    expires_in: int = Field(description="접근 토큰 유효기간")
    access_token_token_expired: datetime = Field(description="액세스 토큰 만료일시")

    def is_expired(self) -> bool:
        return datetime.now() > self.access_token_token_expired


class WebSocket(Auth):
    approval_key: str = Field(description="웹소켓 접속키")
