# kispy

kispy는 한국투자증권(KIS) Developer API를 위한 Python SDK입니다.

## 설치

```bash
pip install git+https://github.com/zeroam/kispy
```

## 기능

- 국내주식 주문/시세 조회
- 해외주식 주문/시세 조회
- 자동 토큰 관리 (만료 시 자동 갱신)
- Rate limiting 지원 (초당 19회)

## 시작하기

### 1. 인증 정보 설정

한국투자증권 Developer > Open API > KIS Developers 에서 API Key를 발급받으세요.

```python
from kispy import KisClient, KisAuth

client = KisClient(
    KisAuth(
        app_key="your_app_key",
        secret="your_app_secret",
        account_no="your_account_no",  # 형식: "12345678-01"
        is_real=True,  # 실전투자: True, 모의투자: False
    )
)
```

### 2. 국내주식

```python
# 현재가 조회
price = client.domestic_stock.quote.get_price("005930")  # 삼성전자

# 매수 주문
result = client.domestic_stock.order.buy(
    stock_code="005930",  # 종목코드
    quantity=10,  # 주문수량
    price=70000,  # 주문가격
)

# 국내주식 현금주문 payload 준비
cash_order = client.domestic_stock.order.prepare_cash_order(
    stock_code="005930",
    side="buy",
    quantity=10,
    price=70000,
    exchange="KRX",
)

# 거래소 구분이 필요한 주문은 KRX / NXT / SOR 중 하나를 명시할 수 있습니다.
nxt_order = client.domestic_stock.order.prepare_cash_order(
    stock_code="005930",
    side="sell",
    quantity=1,
    price=73000,
    exchange="NXT",
)

reservation_order = client.domestic_stock.order.prepare_reservation_order(
    stock_code="005930",
    side="buy",
    quantity=1,
    price=70000,
)

# 로그에는 계좌번호를 가린 payload만 남기세요.
print(cash_order.redacted_body())

# 국내주식 시간외/NXT 시장 데이터 request 준비
overtime_quote = client.domestic_stock.quote.prepare_overtime_asking_price("005930")
after_hour_balance_rank = client.domestic_stock.quote.prepare_after_hour_balance(rank_sort="1")
overtime_conclusion = client.domestic_stock.quote.prepare_time_overtime_conclusion("005930")
nxt_asking_price = client.domestic_stock.realtime.prepare_nxt_asking_price_subscription("005930")
nxt_trade = client.domestic_stock.realtime.prepare_nxt_trade_subscription("005930")
nxt_market_status = client.domestic_stock.realtime.prepare_nxt_market_status_subscription("005930")

print(overtime_quote.params)
print(after_hour_balance_rank.params)
print(overtime_conclusion.params)
print(nxt_asking_price.to_message())

# 일별 시세 조회
history = client.domestic_stock.quote.get_stock_price_history(
    stock_code="005930",
    start_date="2024-01-01",
    end_date="2024-01-31",
)
```

### 3. 해외주식

```python
# 현재가 조회
price = client.overseas_stock.quote.get_price("AAPL")  # Apple Inc.

# 매수 주문
result = client.overseas_stock.order.buy(
    symbol="AAPL",
    exchange_code="NASD",  # NASD: 나스닥, NYSE: 뉴욕, AMEX: 아멕스
    quantity=10,
    price=180.0,
)

# 잔고 조회
balance = client.overseas_stock.account.inquire_balance()

# 일별 시세 조회
history = client.overseas_stock.quote.get_stock_price_history(
    symbol="AAPL",
    exchange="NAS",
    start_date="2024-01-01",
    end_date="2024-01-31",
)
```

## 주의사항

1. 해외주식 서비스는 별도 신청이 필요합니다.
2. 모의투자의 경우 일부 해외 종목만 매매 가능합니다.
3. 거래소별 운영시간을 확인하세요:
   - 미국: 23:30 ~ 06:00 (썸머타임 22:30 ~ 05:00)
   - 일본: 09:00 ~ 11:30, 12:30 ~ 15:00
   - 홍콩: 10:30 ~ 13:00, 14:00 ~ 17:00

## 라이선스

MIT License

## 기여하기

버그 리포트나 기능 요청은 GitHub Issues를 이용해주세요.
Pull Request는 언제나 환영합니다.
