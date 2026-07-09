from types import SimpleNamespace

import pytest

from kispy.client import KisClient
from kispy.exceptions import KispyException
from kispy.overseas_futures.quote import QuoteAPI


def make_quote_api(is_real: bool = True) -> QuoteAPI:
    auth = SimpleNamespace(
        is_real=is_real,
        get_header=lambda: {"authorization": "Bearer token", "appkey": "key", "appsecret": "secret"},
    )
    return QuoteAPI(auth)


def test_kis_client_exposes_overseas_futures_api():
    auth = SimpleNamespace(
        is_real=True,
        cano="12345678",
        acnt_prdt_cd="01",
        account_no="12345678-01",
        get_header=lambda: {"authorization": "Bearer token", "appkey": "key", "appsecret": "secret"},
    )

    client = KisClient(auth)

    assert isinstance(client.overseas_futures.quote, QuoteAPI)


def test_prepare_contract_detail_uses_official_symbol_parameter_slots():
    request = make_quote_api().prepare_contract_detail(["MNQU24", "MESU24"])

    assert request.method == "get"
    assert request.path == "uapi/overseas-futureoption/v1/quotations/search-contract-detail"
    assert request.tr_id == "HHDFC55200000"
    assert request.params["QRY_CNT"] == "2"
    assert request.params["SRS_CD_01"] == "MNQU24"
    assert request.params["SRS_CD_02"] == "MESU24"
    assert request.params["SRS_CD_03"] == ""
    assert request.params["SRS_CD_32"] == ""
    assert "SRS_CD_1" not in request.params


@pytest.mark.parametrize("symbols", [[], [f"SYM{i:02d}" for i in range(33)]])
def test_prepare_contract_detail_rejects_symbol_count_outside_official_range(symbols):
    with pytest.raises(KispyException):
        make_quote_api().prepare_contract_detail(symbols)


def test_get_orderbook_preserves_summary_and_depth_outputs(monkeypatch):
    api = make_quote_api()

    def fake_request(**_kwargs):
        return SimpleNamespace(
            json={
                "rt_cd": "0",
                "output1": {"symbol": "MNQU24", "last": "20000.00"},
                "output2": [{"askp": "20001.00", "bidp": "19999.00"}],
            }
        )

    monkeypatch.setattr(api, "_request", fake_request)

    response = api.get_orderbook("MNQU24")

    assert response == {
        "output1": {"symbol": "MNQU24", "last": "20000.00"},
        "output2": [{"askp": "20001.00", "bidp": "19999.00"}],
    }
