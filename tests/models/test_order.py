from datetime import datetime

from kispy.models.account import Order


def test_order_from_response_buy_completed():
    order = Order.from_response(buy_completed_response)

    assert order.order_id == "0031381228"
    assert order.symbol == "TSLL"
    assert order.side == "buy"
    assert order.status == "closed"
    assert order.requested_price == "19.16000000"
    assert order.requested_quantity == "5"
    assert order.filled_quantity == "5"
    assert order.average_price == "19.16000000"
    assert order.filled_amount == "95.80000"
    assert order.reject_reason == ""
    assert order.order_date == datetime(2024, 11, 8, 5, 46, 48)


def test_order_from_response_sell_completed():
    order = Order.from_response(sell_completed_response)

    assert order.order_id == "0031385365"
    assert order.symbol == "TSLL"
    assert order.side == "sell"
    assert order.status == "closed"
    assert order.requested_price == "19.06000000"
    assert order.requested_quantity == "5"
    assert order.filled_quantity == "5"
    assert order.average_price == "19.06000000"
    assert order.filled_amount == "95.30000"
    assert order.reject_reason == ""
    assert order.order_date == datetime(2024, 11, 8, 6, 1, 48)


def test_order_from_response_canceled():
    order = Order.from_response(canceled_response)

    assert order.order_id == "0030736046"
    assert order.status == "canceled"
    assert order.symbol == "TSLA"
    assert order.side == "buy"
    assert order.requested_price == "0.00000000"
    assert order.requested_quantity == "1"
    assert order.filled_quantity == "0"
    assert order.average_price == "0.00000000"
    assert order.filled_amount == "0.00000"
    assert order.reject_reason == ""
    assert order.order_date == datetime(2024, 8, 1, 4, 30, 19)


def test_order_from_response_expired():
    order = Order.from_response(expired_response)

    assert order.order_id == "0030036440"
    assert order.order_date == datetime(2024, 11, 11, 18, 41, 14)
    assert order.status == "expired"
    assert order.symbol == "TSLL"
    assert order.side == "buy"
    assert order.requested_price == "11.00000000"
    assert order.requested_quantity == "1"
    assert order.filled_quantity == "0"
    assert order.average_price == "0.00000000"
    assert order.filled_amount == "0.00000"
    assert order.reject_reason == "DFD 장종료로 취소"


buy_completed_response = {
    "ord_dt": "20241108",
    "ord_gno_brno": "01790",
    "odno": "0031381228",
    "orgn_odno": "",
    "sll_buy_dvsn_cd": "02",
    "sll_buy_dvsn_cd_name": "매수",
    "rvse_cncl_dvsn": "00",
    "rvse_cncl_dvsn_name": "",
    "pdno": "TSLL",
    "prdt_name": "DIREXION DAILY TSLA BULL 2X SHARES",
    "ft_ord_qty": "5",
    "ft_ord_unpr3": "19.16000000",
    "ft_ccld_qty": "5",
    "ft_ccld_unpr3": "19.16000000",
    "ft_ccld_amt3": "95.80000",
    "nccs_qty": "0",
    "prcs_stat_name": "완료",
    "rjct_rson": "",
    "rjct_rson_name": "",
    "ord_tmd": "054648",
    "tr_mket_name": "나스닥",
    "tr_crcy_cd": "USD",
    "tr_natn": "840",
    "ovrs_excg_cd": "NASD",
    "tr_natn_name": "미국",
    "dmst_ord_dt": "20241109",
    "thco_ord_tmd": "054648",
    "loan_type_cd": "10",
    "loan_dt": "",
    "mdia_dvsn_name": "OpenAPI",
    "usa_amk_exts_rqst_yn": "Y",
}


sell_completed_response = {
    "ord_dt": "20241108",
    "ord_gno_brno": "01790",
    "odno": "0031385365",
    "orgn_odno": "",
    "sll_buy_dvsn_cd": "01",
    "sll_buy_dvsn_cd_name": "매도",
    "rvse_cncl_dvsn": "00",
    "rvse_cncl_dvsn_name": "",
    "pdno": "TSLL",
    "prdt_name": "DIREXION DAILY TSLA BULL 2X SHARES",
    "ft_ord_qty": "5",
    "ft_ord_unpr3": "19.06000000",
    "ft_ccld_qty": "5",
    "ft_ccld_unpr3": "19.06000000",
    "ft_ccld_amt3": "95.30000",
    "nccs_qty": "0",
    "prcs_stat_name": "완료",
    "rjct_rson": "",
    "rjct_rson_name": "",
    "ord_tmd": "060148",
    "tr_mket_name": "나스닥",
    "tr_crcy_cd": "USD",
    "tr_natn": "840",
    "ovrs_excg_cd": "NASD",
    "tr_natn_name": "미국",
    "dmst_ord_dt": "20241109",
    "thco_ord_tmd": "060148",
    "loan_type_cd": "10",
    "loan_dt": "",
    "mdia_dvsn_name": "OpenAPI",
    "usa_amk_exts_rqst_yn": "Y",
}

canceled_response = {
    "ord_dt": "20240801",
    "ord_gno_brno": "01790",
    "odno": "0030736046",
    "orgn_odno": "0030735824",
    "sll_buy_dvsn_cd": "02",
    "sll_buy_dvsn_cd_name": "매수",
    "rvse_cncl_dvsn": "02",
    "rvse_cncl_dvsn_name": "취소",
    "pdno": "TSLA",
    "prdt_name": "테슬라",
    "ft_ord_qty": "1",
    "ft_ord_unpr3": "0.00000000",
    "ft_ccld_qty": "0",
    "ft_ccld_unpr3": "0.00000000",
    "ft_ccld_amt3": "0.00000",
    "nccs_qty": "0",
    "prcs_stat_name": "완료",
    "rjct_rson": "",
    "rjct_rson_name": "",
    "ord_tmd": "043019",
    "tr_mket_name": "나스닥",
    "tr_crcy_cd": "USD",
    "tr_natn": "840",
    "ovrs_excg_cd": "NASD",
    "tr_natn_name": "미국",
    "dmst_ord_dt": "20240802",
    "thco_ord_tmd": "043019",
    "loan_type_cd": "10",
    "loan_dt": "",
    "mdia_dvsn_name": "OpenAPI",
    "usa_amk_exts_rqst_yn": "Y",
}


expired_response = {
    "ord_dt": "20241111",  # 주문접수 일자 (현지시각 기준)
    "ord_gno_brno": "01790",  # 계좌 개설 시 관리점에서 선택한 영업점의 고유번호
    "odno": "0030036440",  # 주문번호
    "orgn_odno": "",  # 정정 또는 취소 대상 주문의 일련번호
    "sll_buy_dvsn_cd": "02",  # 매도매수구분코드 (01: 매도, 02: 매수)
    "sll_buy_dvsn_cd_name": "매수",  # 매도매수구분코드명
    "rvse_cncl_dvsn": "00",  # 취소구분코드 (01: 정정, 02: 취소)
    "rvse_cncl_dvsn_name": "",  # 취소구분코드명
    "pdno": "TSLL",  # 주문종목코드
    "prdt_name": "DIREXION DAILY TSLA BULL 2X SHARES",  # 주문종목명
    "ft_ord_qty": "1",  # 주문수량
    "ft_ord_unpr3": "11.00000000",  # 주문가격
    "ft_ccld_qty": "0",  # 체결수량
    "ft_ccld_unpr3": "0.00000000",  # 체결가격
    "ft_ccld_amt3": "0.00000",  # 체결금액
    "nccs_qty": "0",  # 미체결수량
    "prcs_stat_name": "완료",  # 처리상태명(완료, 거부, 전송)
    "rjct_rson": "",  # 거부사유코드
    "rjct_rson_name": "DFD 장종료로 취소",  # 거부사유명
    "ord_tmd": "184114",  # 주문 접수 시간
    "tr_mket_name": "나스닥",  # 거래시장명
    "tr_crcy_cd": "USD",  # 통화코드
    "tr_natn": "840",  # 국가코드
    "ovrs_excg_cd": "NASD",  # 외국 거래소 코드
    "tr_natn_name": "미국",  # 국가명
    "dmst_ord_dt": "20241111",  # 국내주문일자
    "thco_ord_tmd": "184114",  # 당사주문시각
    "loan_type_cd": "10",  # 대출유형코드
    "loan_dt": "",  # 대출일자
    "mdia_dvsn_name": "OpenAPI",  # 매체구분명
    "usa_amk_exts_rqst_yn": "Y",  # 미국 애프터 마켓 연장 신청여부
}
