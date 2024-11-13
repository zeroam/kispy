from abc import abstractmethod
from typing import Any, Self

from pydantic import BaseModel


class CustomBaseModel(BaseModel):
    @classmethod
    @abstractmethod
    def from_response(cls, item: dict[str, Any]) -> Self:
        """API 응답으로부터 모델 인스턴스를 생성"""
        pass
