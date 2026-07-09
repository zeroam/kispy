"""[해외선물옵션] 기본시세."""

from dataclasses import dataclass

from kispy.base import BaseAPI
from kispy.exceptions import KispyException


@dataclass(frozen=True)
class PreparedOverseasFuturesQuoteRequest:
    method: str
    path: str
    tr_id: str
    params: dict[str, str]
    tr_cont: str = ""


class QuoteAPI(BaseAPI):
    def prepare_stock_detail(self, symbol: str) -> PreparedOverseasFuturesQuoteRequest:
        """해외선물종목상세[v1_해외선물-008]."""
        return PreparedOverseasFuturesQuoteRequest(
            method="get",
            path="uapi/overseas-futureoption/v1/quotations/stock-detail",
            tr_id="HHDFC55010100",
            params={"SRS_CD": symbol},
        )

    def get_stock_detail(self, symbol: str) -> dict:
        data = self._send_prepared_quote_request(self.prepare_stock_detail(symbol))
        return data["output1"]  # type: ignore[no-any-return]

    def prepare_price(self, symbol: str) -> PreparedOverseasFuturesQuoteRequest:
        """해외선물종목현재가[v1_해외선물-009]."""
        return PreparedOverseasFuturesQuoteRequest(
            method="get",
            path="uapi/overseas-futureoption/v1/quotations/inquire-price",
            tr_id="HHDFC55010000",
            params={"SRS_CD": symbol},
        )

    def get_price(self, symbol: str) -> dict:
        data = self._send_prepared_quote_request(self.prepare_price(symbol))
        return data["output1"]  # type: ignore[no-any-return]

    def prepare_orderbook(self, symbol: str) -> PreparedOverseasFuturesQuoteRequest:
        """해외선물 호가[해외선물-031]."""
        return PreparedOverseasFuturesQuoteRequest(
            method="get",
            path="uapi/overseas-futureoption/v1/quotations/inquire-asking-price",
            tr_id="HHDFC86000000",
            params={"SRS_CD": symbol},
        )

    def get_orderbook(self, symbol: str) -> dict:
        data = self._send_prepared_quote_request(self.prepare_orderbook(symbol))
        return {
            "output1": data["output1"],
            "output2": data["output2"],
        }

    def prepare_contract_detail(self, symbols: list[str]) -> PreparedOverseasFuturesQuoteRequest:
        """해외선물 상품기본정보[해외선물-023]."""
        count = len(symbols)
        if not 1 <= count <= 32:
            raise KispyException("종목 개수는 1개 이상 32개 이하여야 합니다.")

        params = {"QRY_CNT": str(count)}
        params.update({f"SRS_CD_{i:02d}": symbols[i - 1] if i <= count else "" for i in range(1, 33)})
        return PreparedOverseasFuturesQuoteRequest(
            method="get",
            path="uapi/overseas-futureoption/v1/quotations/search-contract-detail",
            tr_id="HHDFC55200000",
            params=params,
        )

    def get_contract_detail(self, symbols: list[str]) -> list[dict]:
        data = self._send_prepared_quote_request(self.prepare_contract_detail(symbols))
        return data["output2"]  # type: ignore[no-any-return]

    def _send_prepared_quote_request(self, request: PreparedOverseasFuturesQuoteRequest) -> dict:
        url = f"{self._url}/{request.path}"
        headers = self._auth.get_header()
        headers["tr_id"] = request.tr_id
        headers["tr_cont"] = request.tr_cont
        headers["custtype"] = "P"
        resp = self._request(method=request.method, url=url, headers=headers, params=request.params)
        return resp.json
