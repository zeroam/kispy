from kispy.auth import AuthAPI

from .account import AccountAPI
from .order import OrderAPI
from .quote import QuoteAPI


class OverseasStock:
    def __init__(self, auth: AuthAPI):
        self.account = AccountAPI(auth)
        self.order = OrderAPI(auth)
        self.quote = QuoteAPI(auth)
