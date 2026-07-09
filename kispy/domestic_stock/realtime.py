"""[국내주식] 실시간시세"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PreparedWebSocketSubscription:
    tr_id: str
    tr_type: str
    params: dict[str, str]
    columns: list[str]

    def to_message(self, extra_headers: dict[str, str] | None = None) -> dict:
        headers = {
            "tr_type": self.tr_type,
            "custtype": "P",
        }
        if extra_headers:
            headers.update(extra_headers)

        body_input = {"tr_id": self.tr_id}
        body_input.update(self.params)
        return {
            "header": headers,
            "body": {"input": body_input},
        }


class RealtimeAPI:
    def prepare_nxt_asking_price_subscription(
        self,
        stock_code: str,
        subscribe: bool = True,
    ) -> PreparedWebSocketSubscription:
        return PreparedWebSocketSubscription(
            tr_id="H0NXASP0",
            tr_type=_get_tr_type(subscribe),
            params={"tr_key": stock_code},
            columns=NXT_ASKING_PRICE_COLUMNS,
        )

    def prepare_nxt_trade_subscription(
        self,
        stock_code: str,
        subscribe: bool = True,
    ) -> PreparedWebSocketSubscription:
        return PreparedWebSocketSubscription(
            tr_id="H0NXCNT0",
            tr_type=_get_tr_type(subscribe),
            params={"tr_key": stock_code},
            columns=NXT_TRADE_COLUMNS,
        )

    def prepare_nxt_market_status_subscription(
        self,
        stock_code: str,
        subscribe: bool = True,
    ) -> PreparedWebSocketSubscription:
        return PreparedWebSocketSubscription(
            tr_id="H0NXMKO0",
            tr_type=_get_tr_type(subscribe),
            params={"tr_key": stock_code},
            columns=NXT_MARKET_STATUS_COLUMNS,
        )


def _get_tr_type(subscribe: bool) -> str:
    return "1" if subscribe else "0"


NXT_ASKING_PRICE_COLUMNS = [
    "MKSC_SHRN_ISCD",
    "BSOP_HOUR",
    "HOUR_CLS_CODE",
    "ASKP1",
    "ASKP2",
    "ASKP3",
    "ASKP4",
    "ASKP5",
    "ASKP6",
    "ASKP7",
    "ASKP8",
    "ASKP9",
    "ASKP10",
    "BIDP1",
    "BIDP2",
    "BIDP3",
    "BIDP4",
    "BIDP5",
    "BIDP6",
    "BIDP7",
    "BIDP8",
    "BIDP9",
    "BIDP10",
    "ASKP_RSQN1",
    "ASKP_RSQN2",
    "ASKP_RSQN3",
    "ASKP_RSQN4",
    "ASKP_RSQN5",
    "ASKP_RSQN6",
    "ASKP_RSQN7",
    "ASKP_RSQN8",
    "ASKP_RSQN9",
    "ASKP_RSQN10",
    "BIDP_RSQN1",
    "BIDP_RSQN2",
    "BIDP_RSQN3",
    "BIDP_RSQN4",
    "BIDP_RSQN5",
    "BIDP_RSQN6",
    "BIDP_RSQN7",
    "BIDP_RSQN8",
    "BIDP_RSQN9",
    "BIDP_RSQN10",
    "TOTAL_ASKP_RSQN",
    "TOTAL_BIDP_RSQN",
    "OVTM_TOTAL_ASKP_RSQN",
    "OVTM_TOTAL_BIDP_RSQN",
    "ANTC_CNPR",
    "ANTC_CNQN",
    "ANTC_VOL",
    "ANTC_CNTG_VRSS",
    "ANTC_CNTG_VRSS_SIGN",
    "ANTC_CNTG_PRDY_CTRT",
    "ACML_VOL",
    "TOTAL_ASKP_RSQN_ICDC",
    "TOTAL_BIDP_RSQN_ICDC",
    "OVTM_TOTAL_ASKP_ICDC",
    "OVTM_TOTAL_BIDP_ICDC",
    "STCK_DEAL_CLS_CODE",
    "KMID_PRC",
    "KMID_TOTAL_RSQN",
    "KMID_CLS_CODE",
    "NMID_PRC",
    "NMID_TOTAL_RSQN",
    "NMID_CLS_CODE",
]

NXT_TRADE_COLUMNS = [
    "MKSC_SHRN_ISCD",
    "STCK_CNTG_HOUR",
    "STCK_PRPR",
    "PRDY_VRSS_SIGN",
    "PRDY_VRSS",
    "PRDY_CTRT",
    "WGHN_AVRG_STCK_PRC",
    "STCK_OPRC",
    "STCK_HGPR",
    "STCK_LWPR",
    "ASKP1",
    "BIDP1",
    "CNTG_VOL",
    "ACML_VOL",
    "ACML_TR_PBMN",
    "SELN_CNTG_CSNU",
    "SHNU_CNTG_CSNU",
    "NTBY_CNTG_CSNU",
    "CTTR",
    "SELN_CNTG_SMTN",
    "SHNU_CNTG_SMTN",
    "CNTG_CLS_CODE",
    "SHNU_RATE",
    "PRDY_VOL_VRSS_ACML_VOL_RATE",
    "OPRC_HOUR",
    "OPRC_VRSS_PRPR_SIGN",
    "OPRC_VRSS_PRPR",
    "HGPR_HOUR",
    "HGPR_VRSS_PRPR_SIGN",
    "HGPR_VRSS_PRPR",
    "LWPR_HOUR",
    "LWPR_VRSS_PRPR_SIGN",
    "LWPR_VRSS_PRPR",
    "BSOP_DATE",
    "NEW_MKOP_CLS_CODE",
    "TRHT_YN",
    "ASKP_RSQN1",
    "BIDP_RSQN1",
    "TOTAL_ASKP_RSQN",
    "TOTAL_BIDP_RSQN",
    "VOL_TNRT",
    "PRDY_SMNS_HOUR_ACML_VOL",
    "PRDY_SMNS_HOUR_ACML_VOL_RATE",
    "HOUR_CLS_CODE",
    "MRKT_TRTM_CLS_CODE",
    "VI_STND_PRC",
]

NXT_MARKET_STATUS_COLUMNS = [
    "MKSC_SHRN_ISCD",
    "TRHT_YN",
    "TR_SUSP_REAS_CNTT",
    "MKOP_CLS_CODE",
    "ANTC_MKOP_CLS_CODE",
    "MRKT_TRTM_CLS_CODE",
    "DIVI_APP_CLS_CODE",
    "ISCD_STAT_CLS_CODE",
    "VI_CLS_CODE",
    "OVTM_VI_CLS_CODE",
    "EXCH_CLS_CODE",
]
