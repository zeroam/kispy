from kispy.auth import KisAuth

from .order import OrderAPI
from .quote import QuoteAPI


class DomesticStock:
    def __init__(self, auth: KisAuth):
        self.order = OrderAPI(auth)
        self.quote = QuoteAPI(auth)
