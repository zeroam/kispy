from kispy.auth import AuthAPI

from .order import OrderAPI
from .quote import QuoteAPI


class DomesticStock:
    def __init__(self, auth: AuthAPI):
        self.order = OrderAPI(auth)
        self.quote = QuoteAPI(auth)
