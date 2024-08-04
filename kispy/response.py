import requests

from kispy.exceptions import KispyException


class Response:
    status_code: int
    body: dict

    def __init__(self, resp: requests.Response):
        self.status_code = resp.status_code
        self.body = resp.json()

    def is_success(self) -> bool:
        if self.status_code == 200 and self._return_code == "0":
            return True
        return False

    @property
    def _return_code(self) -> str | None:
        # 토큰 발급시에는 rt_cd가 없음
        if "rt_cd" in self.body:
            return self.body["rt_cd"]  # type: ignore[no-any-return]
        return "0"

    @property
    def _err_code(self) -> str | None:
        if "msg_cd" in self.body:
            return self.body["msg_cd"]  # type: ignore[no-any-return]
        if "error_code" in self.body:
            return self.body["error_code"]  # type: ignore[no-any-return]
        return None

    @property
    def _err_message(self) -> str | None:
        if "msg1" in self.body:
            return self.body["msg1"]  # type: ignore[no-any-return]
        if "error_description" in self.body:
            return self.body["error_description"]  # type: ignore[no-any-return]
        return None

    def raise_for_status(self) -> None:
        if self.is_success():
            return
        raise KispyException(f"{self._err_code}({self.status_code}): {self._err_message}")
