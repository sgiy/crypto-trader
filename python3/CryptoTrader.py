from datetime import datetime
from pprint import pprint

from pydoc import locate
import ipdb

class CryptoTrader:
    def __init__(self, constants = {}):
        self.trader = {}
        self._map_currency_code_to_exchange_code = {}
        self._map_exchange_code_to_currency_code = {}
        self.API_KEYS = constants.get('API_KEYS',{})
        self.EXCHANGE_CURRENCY_RENAME_MAP = constants.get('EXCHANGE_CURRENCY_RENAME_MAP',{})

        for exchange in self.API_KEYS:
            exchange_file = locate('Exchanges.' + exchange)
            exchange_class = getattr(exchange_file, exchange)
            self.trader[exchange] = exchange_class(self.API_KEYS[exchange]['APIKey'], self.API_KEYS[exchange]['Secret'])

        self.init_currencies()
        self.load_active_markets()

    def init_currencies(self):
        self._map_currency_code_to_exchange_code = {}
        self._map_exchange_code_to_currency_code = {}
        for exchange in self.trader:
            currencies = self.trader[exchange].load_currencies()
            self.trader[exchange]._map_currency_code_to_exchange_code = {}
            self._map_exchange_code_to_currency_code[exchange] = {}
            for currency in currencies:
                try:
                    code = currency
                    if exchange in self.EXCHANGE_CURRENCY_RENAME_MAP:
                        if currency in self.EXCHANGE_CURRENCY_RENAME_MAP[exchange]:
                            code = self.EXCHANGE_CURRENCY_RENAME_MAP[exchange][currency]

                    currency_name = currencies[currency]['Name']
                    exchange_name_column = exchange + 'Name'

                    if not code in self._map_currency_code_to_exchange_code:
                        self._map_currency_code_to_exchange_code[code] = {
                            'Name': code
                        }

                    # Populate maps on the exchange object
                    self.trader[exchange]._map_exchange_code_to_currency_code[currency] = code
                    self.trader[exchange]._map_currency_code_to_exchange_code[code] = currency

                    # Populate maps on the CryptoTrader object
                    self._map_exchange_code_to_currency_code[exchange][currency] = code
                    self._map_currency_code_to_exchange_code[code][exchange] = currency
                    self._map_currency_code_to_exchange_code[code][exchange_name_column] = currency_name

                    if code == self._map_currency_code_to_exchange_code[code]['Name']:
                        self._map_currency_code_to_exchange_code[code]['Name'] = currency_name

                except Exception as e:
                    print(str(e))

    def load_active_markets(self):
        self._active_markets = {}
        for exchange in self.trader:
            self.trader[exchange].load_markets()
            for code_base in self.trader[exchange]._active_markets:
                if not code_base in self._active_markets:
                    self._active_markets[code_base] = {}
                for code_curr in self.trader[exchange]._active_markets[code_base]:
                    if not code_curr in self._active_markets[code_base]:
                        self._active_markets[code_base][code_curr] = {}
                    self._active_markets[code_base][code_curr][exchange] = self.trader[exchange]._active_markets[code_base][code_curr]

    def get_market_name(self, exchange, code_base, code_curr):
        return self.trader[exchange]._active_markets[code_base][code_curr]['Market']

    def get_arbitrage_possibilities(self, required_rate_of_return):
        self.load_active_markets()
        self._arbitrage_possibilities = {}
        for code_base in self._active_markets:
            for code_curr in self._active_markets[code_base]:
                markets = self._active_markets[code_base][code_curr]
                best_bid = None
                best_ask = None
                if len(markets) > 1:
                    for exchange in markets:
                        exchange_code = self._map_currency_code_to_exchange_code[code_curr][exchange]
                        if self.trader[exchange]._currencies[exchange_code]['Enabled'] == 1:
                            if not markets[exchange]['Bid'] is None:
                                if best_bid is None or best_bid < markets[exchange]['Bid']:
                                    best_bid = markets[exchange]['Bid']
                            if not markets[exchange]['Ask'] is None:
                                if best_ask is None or best_ask > markets[exchange]['Ask']:
                                    best_ask = markets[exchange]['Ask']
                    if not best_bid is None and not best_ask is None and best_bid > best_ask * required_rate_of_return:
                        if not code_base in self._arbitrage_possibilities:
                            self._arbitrage_possibilities[code_base] = {}
                        self._arbitrage_possibilities[code_base][code_curr] = markets
        return self._arbitrage_possibilities
