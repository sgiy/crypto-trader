from datetime import datetime
from pprint import pprint

from pydoc import locate
import ipdb

class CryptoTrader:
    def __init__(self, API_KEYS):
        self.trader = {}
        for exchange in API_KEYS:
            exchange_file = locate('Exchanges.' + exchange)
            exchange_class = getattr(exchange_file, exchange)
            self.trader[exchange] = exchange_class(API_KEYS[exchange]['APIKey'], API_KEYS[exchange]['Secret'])

        for exchange in self.trader:
            self.trader[exchange].load_currencies()

        for exchange in self.trader:
            self.trader[exchange].load_markets()
