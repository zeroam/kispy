import csv
import io
import zipfile

import requests

from kispy.constants import ExchangeCode, Nation, NationExchangeCodeMap, Symbol


def get_overseas_master_data(exchange_code: ExchangeCode) -> list[dict]:
    url = f"https://new.real.download.dws.co.kr/common/master/{exchange_code.lower()}mst.cod.zip"
    resp = requests.get(url)

    columns = [
        "national_code",  # 국가코드
        "exchange_id",  # 거래소 코드
        "exchange_code",  # 거래소 코드
        "exchange_name",  # 거래소 이름
        "symbol",  # 심볼
        "realtime_symbol",  # 실시간 심볼
        "korean_name",  # 한글 이름
        "english_name",  # 영어 이름 "security_type",  # 종목 유형 (1:지수, 2:주식, 3:ETP(ETF), 4:레버리지/언더라이트)
        "currency",  # 통화
        "float_position",  # 부동 소수점 위치
        "data_type",  # 데이터 유형
        "base_price",  # 기준 가격
        "bid_order_size",  # 매수 주문 크기
        "ask_order_size",  # 매도 주문 크기
        "market_start_time",  # 시장 시작 시간
        "market_end_time",  # 시장 종료 시간
        "dr_yn",  # DR 여부(Y/N)
        "dr_nation_code",  # DR 국가코드
        "industry_classification_code",  # 업종분류코드
        "index_constituent_existence",  # 지수구성종목 존재 여부(0:구성종목없음,1:구성종목있음)
        "tick_size_type",  # Tick size Type
        "classification_code",  # 구분코드(001:ETF,002:ETN,003:ETC,004:Others,005:VIX Underlying ETF,006:VIX Underlying ETN)  # noqa: E501
        "tick_size_type_detail",  # Tick size type 상세
    ]

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zip_file:
        with zip_file.open(f"{exchange_code}mst.cod".upper()) as file:
            text = io.TextIOWrapper(file, encoding="cp949")
            reader = csv.DictReader(text, fieldnames=columns, delimiter="\t")
            return list(reader)


def get_symbol_map(nation: Nation) -> dict[str, Symbol]:
    symbol_map: dict[str, Symbol] = {}
    for exchange_code in NationExchangeCodeMap[nation]:
        master_data = get_overseas_master_data(exchange_code)
        symbol_map.update(
            {
                data["symbol"]: Symbol(
                    symbol=data["symbol"],
                    exchange_code=data["exchange_code"],
                    realtime_symbol=data["realtime_symbol"],
                )
                for data in master_data
            }
        )
    return symbol_map
