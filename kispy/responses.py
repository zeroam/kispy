from typing import Protocol

from kispy.exceptions import KispyErrorResponse, KispyException


class IResponse(Protocol):
    headers: dict
    status_code: int
    json: dict

    def __init__(self, headers: dict, status_code: int, json: dict): ...

    def is_success(self) -> bool: ...

    def raise_for_status(self) -> None: ...


class AuthResponse(IResponse):
    def __init__(self, headers: dict, status_code: int, json: dict):
        self.headers = headers
        self.status_code = status_code
        self.json = json

    def is_success(self) -> bool:
        if self.status_code == 200:
            return True
        return False

    def raise_for_status(self) -> None:
        if self.is_success():
            return
        raise KispyException(f"{self.status_code}: {self.json}")


class BaseResponse(IResponse):
    def __init__(self, headers: dict, status_code: int, json: dict):
        self.headers = headers
        self.status_code = status_code
        self.json = json

    def is_success(self) -> bool:
        if self.status_code == 200 and self._return_code == "0":
            return True
        return False

    @property
    def _return_code(self) -> str:
        # 토큰 발급시에는 rt_cd가 없음
        if "rt_cd" in self.json:
            return self.json["rt_cd"]  # type: ignore[no-any-return]
        return "0"

    @property
    def _err_code(self) -> str:
        if "msg_cd" in self.json:
            return self.json["msg_cd"]  # type: ignore[no-any-return]
        if "error_code" in self.json:
            return self.json["error_code"]  # type: ignore[no-any-return]
        return "0"

    @property
    def _err_message(self) -> str:
        if "msg1" in self.json:
            return self.json["msg1"]  # type: ignore[no-any-return]
        if "error_description" in self.json:
            return self.json["error_description"]  # type: ignore[no-any-return]
        return ""

    def raise_for_status(self) -> None:
        if self.is_success():
            return
        raise KispyErrorResponse(self._err_code, self._err_message)
