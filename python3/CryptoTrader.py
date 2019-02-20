import time, threading
from datetime import datetime
from pprint import pprint

from pydoc import locate
from Exchanges.Coinbase import Coinbase

class CryptoTrader:
    def __init__(self, API_KEYS = {}, SETTINGS = {}):
        self.trader = {}
        self._map_currency_code_to_exchange_code = {}
        self._map_exchange_code_to_currency_code = {}
        self.API_KEYS = API_KEYS
        self.SETTINGS = SETTINGS
        self.init_exchanges()
        self.update_keys()

    def init_exchanges(self):
        for exchange in self.SETTINGS.get('Exchange Classes to Initialize', []):
            exchange_file = locate('Exchanges.' + exchange)
            exchange_class = getattr(exchange_file, exchange)
            self.trader[exchange] = exchange_class()
        print('Initializing Currencies')
        self.init_currencies()
        print('Loading Active Markets')
        self.load_active_markets()

    def update_keys(self):
        self.SETTINGS['Exchanges with API Keys'] =[]
        for exchange in self.API_KEYS.keys():
            self.trader[exchange].update_keys(
                self.API_KEYS[exchange].get('APIKey',''),
                self.API_KEYS[exchange].get('Secret',''),
                self.API_KEYS[exchange].get('APIPassword','')
            )
            if self.API_KEYS[exchange].get('APIKey','') != '':
                self.SETTINGS['Exchanges with API Keys'].append(exchange)

    def init_currencies(self):
        self._map_currency_code_to_exchange_code = {}
        self._map_exchange_code_to_currency_code = {}
        for exchange in self.SETTINGS.get('Exchanges to Load', []):
            print('Loading currencies for ' + exchange)
            t = threading.Thread(target = self.trader[exchange].load_currencies)
            t.start()
            t.join(1)

        for exchange in self.SETTINGS.get('Exchanges to Load', []):
            currencies = self.trader[exchange]._currencies
            self.trader[exchange]._map_currency_code_to_exchange_code = {}
            self._map_exchange_code_to_currency_code[exchange] = {}
            for currency in currencies:
                try:
                    code = currency
                    if exchange in self.SETTINGS.get('Exchange Currency Rename Map',{}):
                        if currency in self.SETTINGS['Exchange Currency Rename Map'][exchange]:
                            code = self.SETTINGS['Exchange Currency Rename Map'][exchange][currency]

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
        for exchange in self.SETTINGS.get('Exchanges to Load', []):
            print('Loading active markets for ' + exchange)
            t = threading.Thread(target = self.trader[exchange].load_markets)
            t.start()
            t.join(1)

        for exchange in self.SETTINGS.get('Exchanges to Load', []):
            for code_base in self.trader[exchange]._active_markets:
                if not code_base in self._active_markets:
                    self._active_markets[code_base] = {}
                for code_curr in self.trader[exchange]._active_markets[code_base]:
                    if not code_curr in self._active_markets[code_base]:
                        self._active_markets[code_base][code_curr] = {}
                    self._active_markets[code_base][code_curr][exchange] = self.trader[exchange]._active_markets[code_base][code_curr]

    def get_currency_code(self, exchange, exchange_code):
        try:
            return self._map_exchange_code_to_currency_code[exchange][exchange_code]
        except Exception as e:
            print('ERROR CryptoTrader get_currency_code',exchange,exchange_code,str(e))
            return None

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
                                    if market3['Ask'] is not None and market2['Ask'] is not None and market1['Bid'] is not None and market3['Ask'] * market2['Ask'] > 0 and market3['Ask'] * market2['Ask'] * required_rate_of_return < market1['Bid']:
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
                                    if market1['Ask'] is not None and market3['Bid'] is not None and market2['Bid'] is not None and market1['Ask'] > 0 and market3['Bid'] * market2['Bid'] > market1['Ask'] * required_rate_of_return:
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

    def calculate_balances_btc(self):
        """
            Load balances from exchanges in BTC terms
            Debug: self._CTMain._Crypto_Trader.calculate_balances_btc()
        """
        self._balances_btc = {}
        for exchange in self.SETTINGS.get('Exchanges with API Keys', []):
            self.trader[exchange].load_balances_btc()
            for currency in self.trader[exchange]._complete_balances_btc:
                try:
                    if self.trader[exchange]._complete_balances_btc[currency]['Total'] > 0:
                        code = self.get_currency_code(exchange, currency)
                        if not 'BtcValue' in self.trader[exchange]._complete_balances_btc[currency]:
                            if code == 'BTC':
                                btc_rate = 1
                            else:
                                if code in ['USD','USDT']:
                                    btc_rate = 2.0 / (self._active_markets[code]['BTC'][exchange]['Bid'] + self._active_markets[code]['BTC'][exchange]['Ask'])
                                else:
                                    btc_rate = (self._active_markets['BTC'][code][exchange]['Bid'] + self._active_markets['BTC'][code][exchange]['Ask']) / 2.0
                            self.trader[exchange]._complete_balances_btc[currency]['BtcValue'] = self.trader[exchange]._complete_balances_btc[currency]['Total'] * btc_rate
                        if not code in self._balances_btc:
                            self._balances_btc[code] = { 'TotalBtcValue': 0.0 }
                        self._balances_btc[code][exchange] = self.trader[exchange]._complete_balances_btc[currency]
                        self._balances_btc[code]['TotalBtcValue'] += self._balances_btc[code][exchange]['BtcValue']
                except Exception as e:
                    print("Error in load_balances_btc for currency " + currency + ": " + str(e))
        return self._balances_btc

    def calculate_balances_btc_totals(self, btc_usd_price = None):
        """
            Load total balances from exchanges
            Debug: self._CTMain._Crypto_Trader.calculate_balances_btc_totals()
        """
        results = {}
        self.calculate_balances_btc()
        for code in self._balances_btc:
            for exchange in self._balances_btc[code]:
                if exchange != 'TotalBtcValue':
                    if not exchange in results:
                        results[exchange] = {'BTC': 0.0}
                    results[exchange]['BTC'] += self._balances_btc[code][exchange]['BtcValue']

        if btc_usd_price is None:
            btc_usd_price = self.trader['Coinbase'].get_btc_usd_price()
        for exchange in results:
            results[exchange]['USD'] = results[exchange]['BTC'] * btc_usd_price
        return results
