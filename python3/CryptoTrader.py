import time
from datetime import datetime
from pprint import pprint

from pydoc import locate

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
        # t = {0: {
        #     'time': time.time()
        # }}
        self._active_markets = {}
        # i = 0
        for exchange in self.trader:
            # i += 1
            # t[i] = {
            #             'time': time.time(),
            #             'exchange': exchange
            #             }
            self.trader[exchange].load_markets()
            for code_base in self.trader[exchange]._active_markets:
                if not code_base in self._active_markets:
                    self._active_markets[code_base] = {}
                for code_curr in self.trader[exchange]._active_markets[code_base]:
                    if not code_curr in self._active_markets[code_base]:
                        self._active_markets[code_base][code_curr] = {}
                    self._active_markets[code_base][code_curr][exchange] = self.trader[exchange]._active_markets[code_base][code_curr]

        # for j in range(i):
        #     print(' Check for exchange {0} took {1:.4f} seconds '.format(t[j+1]['exchange'],t[j+1]['time'] - t[j]['time']))

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

    def get_arbitrage_possibilities_circle(self, required_rate_of_return):
        self.load_active_markets()
        self._arbitrage_possibilities = []
        for code_base1 in self._active_markets:
            for code_curr in self._active_markets[code_base1]:
                for code_base2 in self._active_markets:
                    if code_base1 != code_base2:
                        for exchange in self._active_markets[code_base1][code_curr]:
                            if code_curr in self._active_markets[code_base2] and exchange in self._active_markets[code_base2][code_curr]:
                                if code_base2 in self._active_markets[code_base1] and exchange in self._active_markets[code_base1][code_base2]:
                                    market1 = self._active_markets[code_base1][code_curr][exchange]
                                    market2 = self._active_markets[code_base2][code_curr][exchange]
                                    market3 = self._active_markets[code_base1][code_base2][exchange]
                                    if market3['Ask'] * market2['Ask'] > 0 and market3['Ask'] * market2['Ask'] * required_rate_of_return < market1['Bid']:
                                        self._arbitrage_possibilities.append(
                                            {
                                                'exchange': exchange,
                                                'market1': market1,
                                                'action1': 'sell',
                                                'market2': market2,
                                                'action2': 'buy',
                                                'market3': market3,
                                                'action3': 'buy',
                                                'return': 100.0 * (market1['Bid'] / (market3['Ask'] * market2['Ask']) - 1)
                                            }
                                        )
                                    if market1['Ask'] > 0 and market3['Bid'] * market2['Bid'] > market1['Ask'] * required_rate_of_return:
                                        self._arbitrage_possibilities.append(
                                            {
                                                'exchange': exchange,
                                                'market1': market1,
                                                'action1': 'buy',
                                                'market2': market2,
                                                'action2': 'sell',
                                                'market3': market3,
                                                'action3': 'sell',
                                                'return': 100.0 * (market3['Bid'] * market2['Bid'] / market1['Ask'] - 1)
                                            }
                                        )

        return self._arbitrage_possibilities
